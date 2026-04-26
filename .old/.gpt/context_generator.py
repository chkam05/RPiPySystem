#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Generate a compact Markdown 'context packet' for the RPi modular stack.

What it does:
- Summarizes project tree (ignoring venv/.git/__pycache__/logs/node_modules by default)
- Reads requirements.txt (and compares to installed versions if possible)
- Parses supervisord.conf (programs, eventlisteners, log routing, env)
- Parses nginx vhost (server_name, ports, location blocks -> upstream map)
- Detects Flask and Django services by common files
- Sniffs .env and config.py keys (only names, not secrets)
- Emits a ready-to-paste Markdown file for a new chat

Designed to be safe: does NOT print secret values, only key names.
'''
from __future__ import annotations

import argparse
import configparser
import dataclasses
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Optional, Tuple

# --------------------------------------------------------------------------------
# --- CONFIGURATION ---
# --------------------------------------------------------------------------------

DEFAULT_IGNORE_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "__pycache__", "node_modules",
    "dist", "build", ".mypy_cache", ".pytest_cache", "logs", ".cache"
}

DJANGO_HINT_FILES = {"wsgi.py", "manage.py", "asgi.py"}
FLASK_HINT_FILES = {"app.py", "wsgi.py", "__init__.py"}

# --------------------------------------------------------------------------------
# --- UTILITIES ---
# --------------------------------------------------------------------------------

def rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except Exception:
        return str(p)

def read_text_safe(p: Path, max_bytes: int = 200_000) -> Optional[str]:
    try:
        data = p.read_bytes()
        if len(data) > max_bytes:
            data = data[:max_bytes] + b'\n\n[...truncated...]\n'
        return data.decode('utf-8', 'replace')
    except Exception:
        return None

def shell(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except Exception as e:
        return 127, '', f'{type(e).__name__}: {e}'

def looks_like_flask_dir(d: Path) -> bool:
    # crude heuristic: has app.py or package with Flask() usage
    for name in FLASK_HINT_FILES:
        p = d / name
        if p.exists():
            txt = read_text_safe(p) or ''
            if re.search(r'\bFlask\s*\(', txt):
                return True
    # search controllers folder
    ctrl = d / 'controllers'
    if ctrl.is_dir():
        for py in ctrl.rglob('*.py'):
            txt = read_text_safe(py) or ''
            if 'Blueprint(' in txt or 'Flask(' in txt:
                return True
    return False

def looks_like_django_dir(d: Path) -> bool:
    # wsgi.py with DJANGO_SETTINGS_MODULE or settings.py present
    for cand in [d / 'wsgi.py', d / 'asgi.py', d / 'settings.py']:
        if cand.exists():
            txt = read_text_safe(cand) or ''
            if 'DJANGO_SETTINGS_MODULE' in txt or 'django' in txt.lower():
                return True
    # project folder typically has settings.py inside a subdir
    for sub in d.iterdir() if d.exists() else []:
        if sub.is_dir() and (sub / 'settings.py').exists():
            return True
    return False

def sniff_env_keys(text: str) -> List[str]:
    keys = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k = line.split('=', 1)[0].strip()
            if k and re.match(r'^[A-Z0-9_\.]+$', k):
                keys.append(k)
    return sorted(set(keys))

def sniff_configpy_keys(text: str) -> List[str]:
    keys = []
    for m in re.finditer(r'^\s*([A-Z][A-Z0-9_]+)\s*=', text, re.M):
        keys.append(m.group(1))
    return sorted(set(keys))

# --------------------------------------------------------------------------------
# --- TREE SUMMARY ---
# --------------------------------------------------------------------------------

def build_tree(root: Path, max_depth: int = 3, ignore_dirs: Iterable[str] = DEFAULT_IGNORE_DIRS) -> List[str]:
    lines: List[str] = []
    ignore = set(ignore_dirs)

    def walk(d: Path, depth: int):
        if depth > max_depth:
            return
        try:
            # directories first, then files (alpha)
            entries = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except Exception:
            return
        for e in entries:
            if e.name in ignore:
                continue
            indent = '  ' * depth  # depth=1 -> 2 spaces under 'Katalog główny'
            if e.is_dir():
                # show only the directory name here
                lines.append(f'{indent}📁 {e.name}/')
                walk(e, depth + 1)
            else:
                size = e.stat().st_size if e.exists() else 0
                pretty = f'{size/1024:.0f} KB' if size < 1024*1024 else f'{size/1024/1024:.1f} MB'
                # show only the file name here
                lines.append(f'{indent}📄 {e.name}  ({pretty})')

    lines.append(f'Katalog główny: {root}')
    walk(root, 1)
    return lines

# --------------------------------------------------------------------------------
# --- REQUIREMENTS ---
# --------------------------------------------------------------------------------

def read_requirements(root: Path) -> List[str]:
    for name in ('requirements.txt', 'requirements-prod.txt', 'requirements/base.txt'):
        p = root / name
        if p.exists():
            txt = read_text_safe(p) or ''
            return [line.rstrip() for line in txt.splitlines()]
    return []

def get_installed_versions(packages: Iterable[str]) -> Dict[str, str]:
    pkgs = [p.split('==')[0].split('[',1)[0].strip() for p in packages if p and not p.strip().startswith('#')]
    rc, out, err = shell([sys.executable, '-m', 'pip', 'freeze'])
    result: Dict[str, str] = {}
    if rc == 0:
        for line in out.splitlines():
            if '==' in line:
                n, v = line.split('==', 1)
                result[n.lower()] = v
    # map requested names to installed
    final = {}
    for name in pkgs:
        v = result.get(name.lower())
        if v:
            final[name] = v
    return final

# --------------------------------------------------------------------------------
# --- SUPERVISORD & NGINX PARSING ---
# --------------------------------------------------------------------------------

@dataclasses.dataclass
class Program:
    name: str
    command: str
    stdout: str
    stderr: str
    env: Dict[str, str]

def parse_supervisord_conf(path: Path) -> Tuple[List[Program], List[Program]]:
    # disable interpolation so %(ENV_VIRTUAL_ENV)s stays literal
    cp = configparser.ConfigParser(interpolation=None)
    cp.read(path)
    progs: List[Program] = []
    listeners: List[Program] = []

    def env_map(s: Optional[str]) -> Dict[str, str]:
        if not s:
            return {}
        out = {}
        for part in s.split(','):
            if '=' in part:
                k, v = part.split('=', 1)
                out[k.strip()] = v.strip()
        return out

    for sec in cp.sections():
        if sec.startswith('program:') or sec.startswith('eventlistener:'):
            name = sec.split(':', 1)[1]
            # raw=True avoids any later interpolation attempts just in case
            cmd = cp.get(sec, 'command', fallback='', raw=True)
            so  = cp.get(sec, 'stdout_logfile', fallback='', raw=True)
            se  = cp.get(sec, 'stderr_logfile', fallback='', raw=True)
            env = env_map(cp.get(sec, 'environment', fallback='', raw=True))
            item = Program(name=name, command=cmd, stdout=so, stderr=se, env=env)
            if sec.startswith('program:'):
                progs.append(item)
            else:
                listeners.append(item)
    return progs, listeners

@dataclasses.dataclass
class NginxSummary:
    servers: List[Dict[str, str]]
    locations: List[Dict[str, str]]

def parse_nginx_conf(path: Path) -> NginxSummary:
    txt = read_text_safe(path) or ''
    servers = []
    for m in re.finditer(r'server\s*\{(.*?)\}', txt, re.S):
        block = m.group(1)
        listen = ', '.join(re.findall(r'^\s*listen\s+([^\;]+);', block, re.M))
        server_name = ', '.join(re.findall(r'^\s*server_name\s+([^\;]+);', block, re.M))
        servers.append({'listen': listen.strip(), 'server_name': server_name.strip()})
    locations = []
    for loc, pass_to in re.findall(r'location\s+([^\s\{]+)\s*\{[^}]*?proxy_pass\s+([^\;]+);', txt, re.S):
        locations.append({'location': loc.strip(), 'proxy_pass': pass_to.strip()})
    return NginxSummary(servers=servers, locations=locations)

# --------------------------------------------------------------------------------
# --- SERVICE DETECTION ---
# --------------------------------------------------------------------------------

@dataclasses.dataclass
class ServiceHint:
    path: str
    kind: str   # 'flask' | 'django' | 'unknown'

def detect_services(root: Path) -> List[ServiceHint]:
    hints: List[ServiceHint] = []
    for d in sorted(root.iterdir(), key=lambda p: p.name):
        if not d.is_dir():
            continue
        name = d.name.lower()
        if name.endswith('_service'):
            # dive one level for common app layout
            if looks_like_flask_dir(d) or looks_like_flask_dir(d / d.name.replace('_service', '')):
                hints.append(ServiceHint(path=rel(d, root), kind='flask'))
            elif looks_like_django_dir(d) or looks_like_django_dir(d / d.name.replace('_service', '')):
                hints.append(ServiceHint(path=rel(d, root), kind='django'))
            else:
                hints.append(ServiceHint(path=rel(d, root), kind='unknown'))
    return hints

# --------------------------------------------------------------------------------
# --- MAIN RENDER ---
# --------------------------------------------------------------------------------

MD_HEADER = '''# Projekt aplikacji wieloserwisowej na Raspberry Pi — Pakiet kontekstu
_Ten plik gromadzi minimalny kontekst potrzebny do kontynuacji pracy nad projektem._

'''

def generate_md(root: Path, max_depth: int, git_ignore: bool, extra_files: List[Path]) -> str:
    out: List[str] = [MD_HEADER]

    # Basic meta
    out.append('## Metadane projektu\n')
    out.append(f'- Katalog główny: `{root}`\n')
    rc, pyv, _ = shell([sys.executable, '--version'])
    out.append(f'- Python: `{pyv or sys.version.split()[0]}`\n')

    # Tree
    out.append('\n## Struktura projektu (skrócona)\n')
    tree_lines = build_tree(root, max_depth=max_depth)
    out.append('```\n' + '\n'.join(tree_lines) + '\n```\n')

    # Requirements
    reqs = read_requirements(root)
    out.append('## Wymagania Pythona\n')
    if reqs:
        out.append('`requirements.txt` (wybrane linie):\n')
        out.append('```text\n' + '\n'.join(reqs) + '\n```\n')
        installed = get_installed_versions(reqs)
        if installed:
            out.append('Zainstalowane wersje (wykryte przez `pip freeze`):\n')
            out.append('```text')
            for k, v in sorted(installed.items()):
                out.append(f'{k}=={v}')
            out.append('```\n')
    else:
        out.append('_Nie znaleziono pliku requirements.txt._\n\n')

    # Supervisord
    sup_conf = None
    for cand in ['supervisord.conf', 'supervisor/supervisord.conf', 'conf/supervisord.conf']:
        p = root / cand
        if p.exists():
            sup_conf = p
            break
    out.append('## Podsumowanie Supervisor\n')
    if sup_conf:
        progs, listeners = parse_supervisord_conf(sup_conf)
        out.append(f'- Plik: `{rel(sup_conf, root)}`\n')
        if progs:
            out.append('\n**Programy**:\n')
            for p in progs:
                out.append(f'- `{p.name}` → `{p.command}`')
                if p.stdout or p.stderr:
                    out.append(f'  \n  logi: stdout=`{p.stdout or "default"}`, stderr=`{p.stderr or "default"}`')
                if p.env:
                    out.append('  \n  env: ' + ', '.join(f'{k}={v}' for k,v in p.env.items()))
        if listeners:
            out.append('\n\n**Nasłuchiwacze zdarzeń**:\n')
            for p in listeners:
                out.append(f'- `{p.name}` → `{p.command}`')
                if p.stdout or p.stderr:
                    out.append(f'  \n  logi: stdout=`{p.stdout or "default"}`, stderr=`{p.stderr or "default"}`')
                if p.env:
                    out.append('  \n  env: ' + ', '.join(f'{k}={v}' for k,v in p.env.items()))
        out.append('\n')
    else:
        out.append('_Nie znaleziono pliku supervisord.conf._\n\n')

    # Nginx
    out.append('## Reverse proxy Nginx\n')
    vhost = None
    for cand in ['nginx/pi_stack.conf', '/etc/nginx/sites-available/pi_stack.conf']:
        p = Path(cand)
        if not p.is_absolute():
            p = (root / cand)
        if p.exists():
            vhost = p
            break
    if vhost:
        summary = parse_nginx_conf(vhost)
        out.append(f'- Plik: `{rel(vhost, root)}`\n')
        if summary.servers:
            out.append('**Serwery**:')
            for s in summary.servers:
                out.append(f'\n- listen: `{s["listen"]}`; server_name: `{s["server_name"]}`')
        if summary.locations:
            out.append('\n\n**Lokalizacje (mapowanie proxy)**:')
            for l in summary.locations:
                out.append(f'\n- `{l["location"]}` → `{l["proxy_pass"]}`')
        out.append('\n\n')
    else:
        out.append('_Nie znaleziono vhost Nginx._\n\n')

    # Services
    out.append('## Wykryte serwisy\n')
    hints = detect_services(root)
    if hints:
        for h in hints:
            out.append(f'- `{h.path}` → {h.kind}')
    else:
        out.append('_Nie wykryto katalogów serwisów._')
    out.append('\n\n')

    # Env & config keys (names only)
    out.append('## Klucze konfiguracyjne (tylko nazwy)\n')
    # .env
    env_file = root / '.env'
    if env_file.exists():
        env_txt = read_text_safe(env_file) or ''
        keys = sniff_env_keys(env_txt)
        if keys:
            out.append('- klucze `.env`: ' + ', '.join(keys) + '\n')
    # common per-service config.py
    for svc in ['auth_service', 'bt_service', 'control_service', 'email_service', 'io_service', 'system_service']:
        cfg = root / svc / 'config.py'
        if cfg.exists():
            keys = sniff_configpy_keys(read_text_safe(cfg) or '')
            if keys:
                out.append(f'- `{rel(cfg, root)}`: ' + ', '.join(keys))
                out.append('\n')

    # Extra files (short excerpt)
    if extra_files:
        out.append('\n## Fragmenty plików\n')
        for f in extra_files:
            txt = read_text_safe(f, max_bytes=20_000)
            if txt is None:
                continue
            out.append(f'### `{rel(f, root)}`\n')
            out.append('```text\n' + txt + '\n```\n')

    return '\n'.join(out)

def main():
    ap = argparse.ArgumentParser(description='Generate a Markdown context packet for the project.')
    ap.add_argument('--root', default='.', help='Project root')
    ap.add_argument('--out', default='project_context.md', help='Output Markdown file')
    ap.add_argument('--max-depth', type=int, default=3, help='Max directory depth to include')
    ap.add_argument('--git-ignore', action='store_true', help='(reserved) respect .gitignore (not required here)')
    ap.add_argument('--extra', nargs='*', default=[], help='Extra files to include excerpts from')
    args = ap.parse_args()

    root = Path(args.root).resolve()
    extra = [Path(p).resolve() for p in args.extra]

    md = generate_md(root=root, max_depth=args.max_depth, git_ignore=args.git_ignore, extra_files=extra)

    Path(args.out).write_text(md, encoding='utf-8')

if __name__ == '__main__':
    main()
