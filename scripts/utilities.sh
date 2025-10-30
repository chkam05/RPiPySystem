#!/usr/bin/env bash
# ------------------------------------------------------------------------------
#   Linux bash scripting function library
# ------------------------------------------------------------------------------

# Guard: prevent multiple imports (no short-circuit).
if [ "${__SHLIB_LOADED:-0}" -eq 1 ]; then
    return 0
fi
__SHLIB_LOADED=1


# --- VARIABLES ---

# region LOGO CONTENT
LOGO_CONTENT=$(cat << 'EOF'
 ______   ______   __    _____                       __                            
/      \ /      \ /  |  /     \                     /  |                           
$$$$$$  |$$$$$$  |$$/  /$$$$$  | __   __   ______  _$$ |_     _____   _____  ____  
$$ |_$$ |$$ |_$$ |/  | $$ \_$$/ /  | /  | /      |/ $$   |   /     \ /     \/    \ 
$$   $$< $$   $$/ $$ | $$     \ $$ | $$ |/$$$$$$/ $$$$$$/   /$$$$$  |$$$$$$ $$$$  |
$$$$$$  |$$$$$$/  $$ |  $$$$$  |$$ | $$ |$$     \   $$ | __ $$   $$ |$$ | $$ | $$ |
$$ | $$ |$$ |     $$ | /  \_$$ |$$ \_$$ | $$$$$  |  $$ |/  |$$$$$$$/ $$ | $$ | $$ |
$$ | $$ |$$ |     $$ | $$   $$/ $$   $$ |/    $$/   $$  $$/ $$      |$$ | $$ | $$ |
$$/  $$/ $$/      $$/   $$$$$/   $$$$$$ |$$$$$$/     $$$$/   $$$$$$/ $$/  $$/  $$/ 
                                /  \_$$ |                                          
                                $$   $$/                                           
                                 $$$$$/                                            
EOF
)
# endregion


# ------------------------------------------------------------------------------
# --- IDENTIFICATION FUNCTIONS ---
# ------------------------------------------------------------------------------

# --- Returns the script file name. ---
get_script_name() {
    _basename=$(basename "$0")
    printf '%s\n' "$_basename"
}

# --- Returns the path to the directory where the script file is located. ---
get_script_dir() {
    # Use subshell to not change the caller's CWD.
    (
        CDPATH=
        _dirname=$(dirname "$0")
        if cd -- "$_dirname" 2>/dev/null; then
            pwd -P
            exit 0
        else
            # fallback: zwróć (być może względny) dirname
            printf '%s\n' "$_dirname"
            exit 0
        fi
    )
}

# --- Returns the full path to the script file. ---
get_script_path() {
    case $0 in
        /*)
            # It is already full path.
            printf '%s\n' "$0"
            return 0
            ;;
        */*)
            # Relative path containing '/' - build full path.
            _dir=$(get_script_dir)
            _base=$(basename "$0")
            printf '%s\n' "$_dir/$_base"
            return 0
            ;;
        *)
            # Called by PATH – return literal $0 (without searching the PATH).
            printf '%s\n' "$0"
            return 0
            ;;
    esac
}


# ------------------------------------------------------------------------------
# --- LOGGING FUNCTIONS ---
# ------------------------------------------------------------------------------

# --- Displays an error message in the console. ---
print_error() {
    # Usage: print_error [message] [app_name (prefix)]
    _msg=${1-}
    _app=${2-}

    if [ -z "${_msg}" ]; then
        return 0
    fi

    if [ -z "${_app}" ]; then
        _app=$(get_script_name)
    fi
    
    printf '[%s] ERR: %s\n' "$_app" "$_msg" 1>&2
}

# --- Displays an information message in the console. ---
print_info() {
    # Usage: print_info [message] [app_name (prefix)]
    _msg=${1-}
    _app=${2-}

    if [ -z "${_msg}" ]; then
        return 0
    fi

    if [ -z "${_app}" ]; then
        _app=$(get_script_name)
    fi

    printf '[%s] %s\n' "$_app" "$_msg"
}

# --- Display script logo in the console. ---
print_logo() {
    printf '%s\n\n' "$LOGO_CONTENT"
}

# ------------------------------------------------------------------------------
# --- UTILITY FUNCTIONS ---
# ------------------------------------------------------------------------------

raise_err() {
    # Usage: raise_err [error_message] [error_code] [app_name (prefix)]
    _emsg=${1-}
    _ecode=${2-}
    _app=${3-}
    
    if [ -z "${_ecode}" ]; then
        _ecode=1
    fi

    if [ -n "${_emsg}" ]; then
        print_error "${_app}" "${_emsg}"
    fi

    exit "${_ecode}"
}

# --- Checks if the script was run as root (returns 0, otherwise - 1). ---
is_root() {
    _uid=$( (id -u) 2>/dev/null )

    if [ "$_uid" = "0" ]; then
        return 0
    fi

    return 1
}

