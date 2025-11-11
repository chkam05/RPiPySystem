import os
import re
import subprocess
from time import sleep
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from flask import json

from system_service.models.system.cpu_info import CPUInfo
from system_service.models.system.cpu_usage import CPUUsage
from system_service.models.system.disk_type import DiskType
from system_service.models.system.disk_usage import DiskUsage
from system_service.models.system.mem_usage import MemUsage
from system_service.models.system.os_temp_info import OSTempInfo
from system_service.models.system.os_usage import OSUsage


class OSUsageResolver:
    """
    Collects current system usage stats (CPU/MEM/DISKS/TEMP) without requiring root.
    """

    # -------- Paths --------
    CPUINFO_PATH: ClassVar[str] = '/proc/cpuinfo'
    PROC_STAT_PATH: ClassVar[str] = '/proc/stat'
    MEMINFO_PATH: ClassVar[str] = '/proc/meminfo'
    THERMAL_BASE: ClassVar[str] = '/sys/class/thermal'
    HWMON_BASE: ClassVar[str] = '/sys/class/hwmon'
    CPU0_FREQ_PATH: ClassVar[str] = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq'
    CPU0_MIN_FREQ_PATH: ClassVar[str] = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq'
    CPU0_MAX_FREQ_PATH: ClassVar[str] = '/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq'
    CPU0_INFO_MIN_FREQ_PATH: ClassVar[str] = '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_min_freq'
    CPU0_INFO_MAX_FREQ_PATH: ClassVar[str] = '/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq'

    # -------- Commands (no sudo) --------
    CMD_UNAME_M: ClassVar[List[str]] = ['uname', '-m']
    CMD_NPROC: ClassVar[List[str]] = ['nproc']
    CMD_LSCPU: ClassVar[List[str]] = ['lscpu']
    CMD_LSBLK: ClassVar[List[str]] = ['lsblk', '-J', '-b', '-o', 'NAME,LABEL,UUID,FSTYPE,SIZE,MOUNTPOINT,TYPE']
    CMD_DF: ClassVar[List[str]] = ['df', '-B1', '--output=source,used,avail,size,target']

    # -------- Regex patterns --------
    RE_MODEL_NAME: ClassVar[re.Pattern] = re.compile(r'^model name\s*:\s*(.+)$', re.MULTILINE)
    RE_MODEL_PROC: ClassVar[re.Pattern] = re.compile(r'^Processor\s*:\s*(.+)$', re.MULTILINE)  # ARM alt
    RE_LSCPU_MODEL_NAME: ClassVar[re.Pattern] = re.compile(r'^Model name:\s+(.+)$', re.MULTILINE)
    RE_LSCPU_SOCKETS: ClassVar[re.Pattern] = re.compile(r'^Socket\(s\):\s+(\d+)$', re.MULTILINE)
    RE_LSCPU_CORES_PER_SOCKET: ClassVar[re.Pattern] = re.compile(r'^Core\(s\) per socket:\s+(\d+)$', re.MULTILINE)
    RE_LSCPU_CPU_MHZ: ClassVar[re.Pattern] = re.compile(r'^CPU MHz:\s+([0-9.]+)$', re.MULTILINE)
    RE_LSCPU_CPU_MIN_MHZ: ClassVar[re.Pattern] = re.compile(r'^CPU min MHz:\s+([0-9.]+)$', re.MULTILINE)
    RE_LSCPU_CPU_MAX_MHZ: ClassVar[re.Pattern] = re.compile(r'^CPU max MHz:\s+([0-9.]+)$', re.MULTILINE)
    RE_MEMINFO_LINE: ClassVar[re.Pattern] = re.compile(r'^(\w+):\s+(\d+)')
    RE_DF_SPLIT: ClassVar[re.Pattern] = re.compile(r'\s+')

    # -------- Tunables --------
    CPU_SAMPLE_SECONDS: ClassVar[float] = 3.0
    CPU_SAMPLE_MIN: ClassVar[float] = 1.0
    CPU_SAMPLE_MAX: ClassVar[float] = 5.0


    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation of this static utility class.
        """
        raise TypeError(f'{cls.__name__} is a static utility class and cannot be instantiated.')
    

    # --------------------------------------------------------------------------
    # --- GLOBAL HELPERS (Generic for future extensions) ---
    # --------------------------------------------------------------------------

    @staticmethod
    def _run_cmd(args: List[str]) -> Optional[str]:
        """
        Run command and return stdout as string, or None.
        """
        try:
            out = subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)
            return out.strip() if out else None
        except Exception:
            return None

    @staticmethod
    def _read_text(path: str) -> Optional[str]:
        """
        Read whole file content as UTF-8 text, or None.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    # --------------------------------------------------------------------------
    # --- CPU INFO ---
    # --------------------------------------------------------------------------

    @classmethod
    def _extract_model_from_lscpu(cls, lscpu_text: str) -> Optional[str]:
        """
        Extract CPU model from lscpu output (preferred on ARM).
        """
        if not lscpu_text:
            return None
        
        m = cls.RE_LSCPU_MODEL_NAME.search(lscpu_text)
        return m.group(1).strip() if m else None

    @classmethod
    def _extract_model_from_cpuinfo(cls, cpuinfo: str) -> Optional[str]:
        """
        Extract CPU model from /proc/cpuinfo (avoid board 'Model:').
        """
        if not cpuinfo:
            return None
        
        m = cls.RE_MODEL_NAME.search(cpuinfo)
        if m:
            return m.group(1).strip()
        
        m = cls.RE_MODEL_PROC.search(cpuinfo)
        return m.group(1).strip() if m else None
    
    @classmethod
    def _get_architecture(cls) -> Optional[str]:
        """
        Return machine architecture from uname -m.
        """
        return cls._run_cmd(cls.CMD_UNAME_M)
    
    @classmethod
    def _get_logical_cores(cls) -> Optional[int]:
        """
        Return logical CPU count from nproc.
        """
        s = cls._run_cmd(cls.CMD_NPROC)

        try:
            return int(s) if s else None
        except Exception:
            return None
    
    @classmethod
    def _get_physical_cores(cls, lscpu_text: Optional[str]) -> Optional[int]:
        """
        Estimate physical cores from lscpu output (sockets * cores per socket).
        """
        if not lscpu_text:
            return None
        
        m1 = cls.RE_LSCPU_SOCKETS.search(lscpu_text)
        m2 = cls.RE_LSCPU_CORES_PER_SOCKET.search(lscpu_text)

        if not (m1 and m2):
            return None
        
        try:
            return int(m1.group(1)) * int(m2.group(1))
        except Exception:
            return None
    
    @classmethod
    def _read_cpufreq_khz(cls, path: str) -> Optional[int]:
        """
        Read cpufreq value from sysfs (kHz).
        """
        s = cls._read_text(path)
        if not s:
            return None
        
        s = s.strip()
        if not s.isdigit():
            return None
        
        try:
            return int(s)
        except Exception:
            return None

    @classmethod
    def _get_cpu_freq(cls, lscpu_text: Optional[str]) -> Optional[float]:
        """
        Read current CPU frequency (MHz) from sysfs or lscpu.
        """
        khz = cls._read_cpufreq_khz(cls.CPU0_FREQ_PATH)

        if khz is not None:
            return khz / 1000.0
        
        if not lscpu_text:
            lscpu_text = cls._run_cmd(cls.CMD_LSCPU) or ''

        m = cls.RE_LSCPU_CPU_MHZ.search(lscpu_text)

        if m:
            try:
                return float(m.group(1))
            except Exception:
                return None
        return None

    @classmethod
    def _get_cpu_freq_bounds(cls, lscpu_text: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        """
        Read min/max CPU frequency (MHz) from cpufreq sysfs; fallback to lscpu.
        """
        min_khz = (
            cls._read_cpufreq_khz(cls.CPU0_INFO_MIN_FREQ_PATH)
            or cls._read_cpufreq_khz(cls.CPU0_MIN_FREQ_PATH)
        )

        max_khz = (
            cls._read_cpufreq_khz(cls.CPU0_INFO_MAX_FREQ_PATH)
            or cls._read_cpufreq_khz(cls.CPU0_MAX_FREQ_PATH)
        )

        min_mhz = min_khz / 1000.0 if isinstance(min_khz, int) else None
        max_mhz = max_khz / 1000.0 if isinstance(max_khz, int) else None

        if (min_mhz is None or max_mhz is None):
            text = lscpu_text or cls._run_cmd(cls.CMD_LSCPU) or ''
            if min_mhz is None:
                m1 = cls.RE_LSCPU_CPU_MIN_MHZ.search(text)

                if m1:
                    try:
                        min_mhz = float(m1.group(1))
                    except Exception:
                        pass
            
            if max_mhz is None:
                m2 = cls.RE_LSCPU_CPU_MAX_MHZ.search(text)

                if m2:
                    try:
                        max_mhz = float(m2.group(1))
                    except Exception:
                        pass
        return min_mhz, max_mhz

    @classmethod
    def get_cpu_info(cls) -> CPUInfo:
        """
        Build ProcInfo using lscpu (preferred) + /proc/cpuinfo + cpufreq.
        """
        cpuinfo = cls._read_text(cls.CPUINFO_PATH) or ''
        lscpu = cls._run_cmd(cls.CMD_LSCPU) or ''

        model = cls._extract_model_from_lscpu(lscpu) or cls._extract_model_from_cpuinfo(cpuinfo)

        freq_cur = cls._get_cpu_freq(lscpu)
        freq_min, freq_max = cls._get_cpu_freq_bounds(lscpu)

        return CPUInfo(
            model=model,
            architecture=cls._get_architecture(),
            cores_logical=cls._get_logical_cores(),
            cores_physical=cls._get_physical_cores(lscpu),
            freq=freq_cur,
            freq_min=freq_min,
            freq_max=freq_max,
        )
    
    # --------------------------------------------------------------------------
    # --- CPU USAGE (total + per-thread) ---
    # --------------------------------------------------------------------------

    @classmethod
    def _read_proc_stat_snapshot(cls) -> Tuple[Dict[str, Tuple[int, int, int]], List[str]]:
        """
        Take a /proc/stat snapshot: returns map {cpu*: (total, idle_all, non_idle)} and ordered cpu keys.
        """
        out: Dict[str, Tuple[int, int, int]] = {}
        order: List[str] = []

        try:
            with open(cls.PROC_STAT_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.startswith('cpu'):
                        continue
                    parts = line.split()
                    key = parts[0]          # 'cpu', 'cpu0', ...
                    vals: List[int] = []

                    for x in parts[1:]:
                        try:
                            vals.append(int(x))
                        except Exception:
                            vals.append(0)
                    
                    while len(vals) < 10:
                        vals.append(0)

                    user, nice, system, idle, iowait, irq, softirq, steal, guest, guest_nice = vals[:10]

                    idle_all = idle + iowait
                    non_idle = (user + nice + system + irq + softirq + steal) 
                    total = idle_all + non_idle

                    out[key] = (total, idle_all, non_idle)
                    order.append(key)
        except Exception:
            pass
        return out, order

    @staticmethod
    def _cpu_usage_pct(
        s1: Dict[str, Tuple[int, int, int]],
        s2: Dict[str, Tuple[int, int, int]], key: str
    ) -> Optional[float]:
        """
        Compute usage percent for a given cpu key using two /proc/stat snapshots.
        """
        if key not in s1 or key not in s2:
            return None
        
        t1, idle1, non1 = s1[key]
        t2, idle2, non2 = s2[key]

        dt = t2 - t1
        dnon = non2 - non1
        didle = idle2 - idle1

        if dt <= 0:
            return None

        # usage = dnon / dt * 100; clamp.
        usage = (max(0, dnon) / float(dt)) * 100.0
        if usage < 0.0:
            usage = 0.0
        elif usage > 100.0:
            usage = 100.0
        return usage

    @classmethod
    def _take_two_cpu_snapshots(
        cls,
        target_seconds: float,
        exact: bool
    ) -> Tuple[Dict[str, Tuple[int, int, int]], Dict[str, Tuple[int, int, int]], List[str]]:
        """
        Adaptively take two /proc/stat snapshots ensuring enough jiffy delta for stable %.
        """
        if exact:
            wait_time = max(cls.CPU_SAMPLE_MIN, min(target_seconds, cls.CPU_SAMPLE_MAX))
            s1, order = cls._read_proc_stat_snapshot()
            sleep(wait_time)
            s2, _ = cls._read_proc_stat_snapshot()
            return s1, s2, order

        # Clamp requested window.
        target_seconds = max(cls.CPU_SAMPLE_MIN, min(target_seconds, cls.CPU_SAMPLE_MAX))

        # Get kernel HZ.
        try:
            hz = os.sysconf('SC_CLK_TCK')   # Commonly 100
        except (AttributeError, ValueError):
            hz = 100

        # Aim for at least this many jiffies to avoid quantization.
        min_jiffies = max(8, int(0.3 * hz))     # ~30% seconds or minutes. 8 ticks.

        s1, order = cls._read_proc_stat_snapshot()
        waited = 0.0
        step = min(0.05, target_seconds)        # 50ms short
        max_wait = max(target_seconds, 0.75)    # Let the window extend slightly.

        while True:
            sleep(step)
            waited += step
            s2, _ = cls._read_proc_stat_snapshot()
            t1, _, _ = s1.get('cpu', (0, 0, 0))
            t2, _, _ = s2.get('cpu', (0, 0, 0))
            dt = t2 - t1
            if dt >= min_jiffies or waited >= max_wait:
                return s1, s2, order

    @classmethod
    def _compute_cpu_usage(
        cls,
        target_seconds: float,
        exact: bool
    ) -> Tuple[Optional[float], Dict[str, float]]:
        """
        Compute total and per-cpu usage.
        """
        s1, s2, order = cls._take_two_cpu_snapshots(target_seconds, exact)
        total_v = cls._cpu_usage_pct(s1, s2, 'cpu')
        per: Dict[str, float] = {}

        for k in order:
            if k == 'cpu':
                continue
            v = cls._cpu_usage_pct(s1, s2, k)
            if v is not None:
                per[k] = round(v, 1)

        total_v = round(total_v, 1) if total_v is not None else None
        return total_v, per

    @classmethod
    def _compute_cpu_usage_with_retry(
        cls,
        target_seconds: float,
        exact: bool
    ) -> Tuple[Optional[float], Dict[str, float]]:
        """
        Compute total and per-cpu usage; if all zeros, retry once with a longer window.
        """
        # First try with requested window.
        total_v, per = cls._compute_cpu_usage(target_seconds, exact)
        if total_v is None:
            return None, per

        # If everything is (near) zero, retry with a longer window once.
        if total_v == 0.0 and all(v == 0.0 for v in per.values()):
            longer = min(max(target_seconds * 2.0, 0.5), cls.CPU_SAMPLE_MAX)
            total_v, per = cls._compute_cpu_usage(longer, exact)

        return total_v, per

    @classmethod
    def get_cpu_usage(cls, sample_seconds: float, exact: bool = False) -> CPUUsage:
        """
        Get both total and per-CPU usage from a single sampling window.
        """
        cpu_total, cpu_per_core = cls._compute_cpu_usage_with_retry(sample_seconds, exact)

        return CPUUsage(
            cores=cpu_per_core,
            total=cpu_total
        )

    # --------------------------------------------------------------------------
    # --- CPU TEMPERATURE ---
    # --------------------------------------------------------------------------

    @classmethod
    def _normalize_temp_value(cls, raw: float) -> float:
        """
        Normalize thermal value to Celsius (heuristic).
        """
        return raw / 1000.0 if raw > 200 else raw
    
    @classmethod
    def _read_temperature(cls) -> Optional[float]:
        """
        Return current temperature (°C): prefer CPU/SOC; else hottest available.
        """
        readings: List[Tuple[str, float]] = []

        # 1) thermal zones: /sys/class/thermal/thermal_zone*/{type,temp}.
        if os.path.isdir(cls.THERMAL_BASE):
            try:
                for name in os.listdir(cls.THERMAL_BASE):
                    if not name.startswith('thermal_zone'):
                        continue
                    zdir = os.path.join(cls.THERMAL_BASE, name)
                    ttype = (cls._read_text(os.path.join(zdir, 'type')) or '').strip().lower()
                    tval = cls._read_text(os.path.join(zdir, 'temp'))
                    if not tval:
                        continue
                    try:
                        val = cls._normalize_temp_value(float(tval.strip()))
                        readings.append((ttype, val))
                    except Exception:
                        continue
            except Exception:
                pass

        # 2) hwmon inputs: /sys/class/hwmon/hwmon*/temp*_input (often the same source).
        if os.path.isdir(cls.HWMON_BASE):
            try:
                for hw in os.listdir(cls.HWMON_BASE):
                    hwdir = os.path.join(cls.HWMON_BASE, hw)
                    if not os.path.isdir(hwdir):
                        continue
                    
                    labels: Dict[str, str] = {}
                    for fname in os.listdir(hwdir):
                        if fname.startswith('temp') and fname.endswith('_label'):
                            idx = fname[len('temp'):-len('_label')]
                            labels[idx] = (cls._read_text(os.path.join(hwdir, fname)) or '').strip().lower()
                    
                    for fname in os.listdir(hwdir):
                        if not (fname.startswith('temp') and fname.endswith('_input')):
                            continue
                        idx = fname[len('temp'):-len('_input')]
                        val_s = cls._read_text(os.path.join(hwdir, fname))
                        if not val_s:
                            continue
                        try:
                            val = cls._normalize_temp_value(float(val_s.strip()))
                        except Exception:
                            continue
                        label = labels.get(idx, '')
                        readings.append((label, val))
            except Exception:
                pass

        if not readings:
            return None

        # CPU/SOC
        for label, val in readings:
            if any(x in label for x in ('cpu', 'soc', 'core', 'package')):
                return val

        # fallback: highest available
        return max(val for _, val in readings)

    @classmethod
    def _read_max_temperature(cls) -> Optional[float]:
        """
        Return maximum allowed (critical) temperature in °C (lowest among available limits).
        """
        limits: List[float] = []

        # 1) thermal trip points: crit/critical/hot
        if os.path.isdir(cls.THERMAL_BASE):
            try:
                for name in os.listdir(cls.THERMAL_BASE):
                    if not name.startswith('thermal_zone'):
                        continue
                    zdir = os.path.join(cls.THERMAL_BASE, name)
                    for idx in range(0, 16):
                        t_type_path = os.path.join(zdir, f'trip_point_{idx}_type')
                        t_temp_path = os.path.join(zdir, f'trip_point_{idx}_temp')
                        if not (os.path.exists(t_type_path) and os.path.exists(t_temp_path)):
                            continue
                        ttype = (cls._read_text(t_type_path) or '').strip().lower()
                        if ttype not in ('crit', 'critical', 'hot'):
                            continue
                        tval = cls._read_text(t_temp_path)
                        if not tval:
                            continue
                        try:
                            limits.append(cls._normalize_temp_value(float(tval.strip())))
                        except Exception:
                            continue
            except Exception:
                pass

        # 2) hwmon limits: temp*_crit / temp*_max
        if os.path.isdir(cls.HWMON_BASE):
            try:
                for hw in os.listdir(cls.HWMON_BASE):
                    hwdir = os.path.join(cls.HWMON_BASE, hw)
                    if not os.path.isdir(hwdir):
                        continue
                    for fname in os.listdir(hwdir):
                        if not fname.startswith('temp'):
                            continue
                        if not (fname.endswith('_crit') or fname.endswith('_max')):
                            continue
                        val_s = cls._read_text(os.path.join(hwdir, fname))
                        if not val_s:
                            continue
                        try:
                            limits.append(cls._normalize_temp_value(float(val_s.strip())))
                        except Exception:
                            continue
            except Exception:
                pass

        if not limits:
            return None

        return min(limits)
    
    @classmethod
    def get_temperature(cls) -> OSTempInfo:
        """
        Return current and maximum allowed temperatures (°C).
        """
        max_temp_c = cls._read_max_temperature()
        temp_c = cls._read_temperature()

        return OSTempInfo(
            max_temp_c=max_temp_c,
            temp_c=temp_c
        )

    # --------------------------------------------------------------------------
    # --- MEMORY INFO/USAGE ---
    # --------------------------------------------------------------------------

    @classmethod
    def _read_meminfo_kv(cls) -> Dict[str, int]:
        """
        Read /proc/meminfo into a {Key: kB} dict.
        """
        text = cls._read_text(cls.MEMINFO_PATH) or ''
        kv: Dict[str, int] = {}

        for ln in text.splitlines():
            m = cls.RE_MEMINFO_LINE.match(ln)
            if not m:
                continue

            try:
                kv[m.group(1)] = int(m.group(2))  # kB
            except Exception:
                continue
        return kv
    
    @staticmethod
    def _kb_to_mb(x: Optional[int]) -> Optional[int]:
        """
        Convert kB to MB (rounded).
        """
        return int(round(x / 1024.0)) if isinstance(x, int) else None
    
    @classmethod
    def _compute_mem_usage_from_kv(cls, kv: Dict[str, int]) -> MemUsage:
        """
        Compute MemUsage fields from /proc/meminfo key-values.
        """
        total = kv.get('MemTotal')
        free = kv.get('MemFree')
        available = kv.get('MemAvailable')
        buffers = kv.get('Buffers')
        cached = kv.get('Cached')
        srecl = kv.get('SReclaimable')
        shmem = kv.get('Shmem')
        swap_total = kv.get('SwapTotal')
        swap_free = kv.get('SwapFree')

        bc_kb = (buffers or 0) + (cached or 0) + (srecl or 0)

        if total is not None and free is not None:
            used_kb = max(0, total - free - bc_kb)
        else:
            used_kb = None

        if available is None:
            avail_kb = (free or 0) + bc_kb if (free is not None) else None
        else:
            avail_kb = available
        
        total_all_kb = (total or 0) + (swap_total or 0) if (total is not None and swap_total is not None) else None
        free_all_kb = None
        used_all_kb = None

        if used_kb is not None and swap_total is not None and swap_free is not None:
            swap_used_kb = swap_total - swap_free
            used_all_kb = used_kb + swap_used_kb
        
        if free is not None and swap_free is not None:
            free_all_kb = free + swap_free
        
        swap_used = (swap_total - swap_free) if (swap_total is not None and swap_free is not None) else None

        return MemUsage(
            total=cls._kb_to_mb(total),
            free=cls._kb_to_mb(free),
            used=cls._kb_to_mb(used_kb),
            available=cls._kb_to_mb(avail_kb),
            buff_cache=cls._kb_to_mb(bc_kb),
            shared=cls._kb_to_mb(shmem),
            swap_total=cls._kb_to_mb(swap_total),
            swap_free=cls._kb_to_mb(swap_free),
            swap_used=cls._kb_to_mb(swap_used),
            sum_total=cls._kb_to_mb(total_all_kb),
            sum_free=cls._kb_to_mb(free_all_kb),
            sum_used=cls._kb_to_mb(used_all_kb),
        )
    
    @classmethod
    def get_memory_usage(cls) -> MemUsage:
        """
        Return MemUsage computed from /proc/meminfo.
        """
        kv = cls._read_meminfo_kv()

        if kv:
            return cls._compute_mem_usage_from_kv(kv)
        
        return MemUsage()
    
    # --------------------------------------------------------------------------
    # --- DISKS INFO/USAGE ---
    # --------------------------------------------------------------------------

    @classmethod
    def _map_fs_type(cls, fs: Optional[str]) -> DiskType:
        """
        Map filesystem string to DiskType enum.
        """
        if not fs:
            return DiskType.OTHER
        
        val = fs.lower()

        try:
            return DiskType(val)
        except Exception:
            return DiskType.SWAP if val in ('swap', 'linux-swap') else DiskType.OTHER
    
    @classmethod
    def _b_to_mb(cls, x: Optional[int]) -> Optional[int]:
        """
        Convert bytes to MB (rounded).
        """
        return int(round(x / (1024 * 1024))) if isinstance(x, int) else None
    
    @classmethod
    def _df_usage_map(cls) -> Dict[str, Dict[str, int]]:
        """
        Build a map from device and mountpoint to usage dict (bytes).
        """
        out = cls._run_cmd(cls.CMD_DF)
        result: Dict[str, Dict[str, int]] = {}

        if not out:
            return result
        
        lines = [ln for ln in out.splitlines() if ln.strip()]
        for ln in lines[1:]:
            parts = cls.RE_DF_SPLIT.split(ln.strip(), maxsplit=4)
            if len(parts) < 5:
                continue

            src, used, avail, size, target = parts
            try:
                used_b, avail_b, size_b = int(used), int(avail), int(size)
            except Exception:
                continue

            result[src] = {'used': used_b, 'avail': avail_b, 'size': size_b, 'target': target}
            result[target] = {'used': used_b, 'avail': avail_b, 'size': size_b, 'source': src}
        return result
    
    @classmethod
    def _walk_lsblk_tree(cls, nodes: List[Dict[str, Any]], dfmap: Dict[str, Dict[str, int]], acc: List[DiskUsage]) -> None:
        """
        Walk lsblk JSON tree and append DiskUsage entries.
        """
        for n in nodes:
            name = n.get('name')
            ntype = (n.get('type') or '').lower()
            fstype = n.get('fstype')
            label = n.get('label')
            uuid = n.get('uuid')
            size_b = n.get('size')
            mnt = n.get('mountpoint')

            if ntype in ('disk', 'part') and (fstype or mnt or ntype == 'part'):
                used_b = free_b = None
                if mnt and mnt in dfmap:
                    used_b = dfmap[mnt]['used']
                    free_b = dfmap[mnt]['avail']
                    size_b = dfmap[mnt]['size']
                elif name and f'/dev/{name}' in dfmap:
                    used_b = dfmap[f'/dev/{name}']['used']
                    free_b = dfmap[f'/dev/{name}']['avail']
                    size_b = dfmap[f'/dev/{name}']['size']

                if (fstype or '').lower() in ('swap', 'linux-swap') and not mnt:
                    mnt = '[SWAP]'

                acc.append(
                    DiskUsage(
                        dev_name=name,
                        label=label,
                        uuid=uuid,
                        fs_type=cls._map_fs_type(fstype),
                        size_mb=cls._b_to_mb(size_b if isinstance(size_b, int) else None),
                        used_mb=cls._b_to_mb(used_b),
                        free_mb=cls._b_to_mb(free_b),
                        mount_point=mnt,
                    )
                )

            if isinstance(n.get('children'), list):
                cls._walk_lsblk_tree(n['children'], dfmap, acc)
    
    @classmethod
    def get_disks(cls) -> List[DiskUsage]:
        """
        Collect DiskUsage list combining lsblk metadata with df usage.
        """
        dfmap = cls._df_usage_map()
        lsblk_out = cls._run_cmd(cls.CMD_LSBLK)
        disks: List[DiskUsage] = []
        
        if not lsblk_out:
            return disks
        
        try:
            tree = json.loads(lsblk_out)
        except Exception:
            return disks
        
        cls._walk_lsblk_tree(tree.get('blockdevices', []) or [], dfmap, disks)
        return disks
    
    # --------------------------------------------------------------------------
    # --- OVERALL OS USAGE ---
    # --------------------------------------------------------------------------

    @classmethod
    def get_os_usage(cls, sample_seconds: int = CPU_SAMPLE_SECONDS) -> OSUsage:
        """
        Return consolidated OSUsage snapshot.
        """
        cpu_usage = cls.get_cpu_usage(sample_seconds, False)
        cpu = cls.get_cpu_info()
        temperature = cls.get_temperature()
        mem = cls.get_memory_usage()
        disks = cls.get_disks()
        
        return OSUsage(
            cpu=cpu,
            cpu_usage=cpu_usage,
            temperature=temperature,
            memory=mem,
            disks=disks
        )