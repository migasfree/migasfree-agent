import os
import shutil
import subprocess
import sys

# HKLM App Paths key location
APP_PATHS_KEY = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths'
EXE_NAME = 'migasfree-agent.exe'
SHIM_NAME = 'migasfree-agent.cmd'
SERVICE_NAME = 'migasfree-agent'


def remove_from_registry(exe_name: str) -> bool:
    """Removes the specified executable from the Windows App Paths registry."""
    if sys.platform != 'win32':
        return True

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, APP_PATHS_KEY, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                winreg.DeleteKey(key, exe_name)
                print(f"Successfully removed '{exe_name}' from Windows App Paths.")
            except FileNotFoundError:
                print(f"'{exe_name}' was not found in App Paths (or already removed).")
            except PermissionError:
                print(
                    f"Permission denied: Unable to delete '{exe_name}' from App Paths. Run as Administrator.",
                    file=sys.stderr,
                )
                return False
    except Exception as e:
        print(f'Error opening Registry App Paths: {e}', file=sys.stderr)
        return False
    return True


def get_wpt_bin_dir() -> str:
    """Finds the directory where wpt is installed."""
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for d in path_dirs:
        if os.path.exists(os.path.join(d, 'wpt.exe')):
            return d

    program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    wpt_default = os.path.join(program_files, 'wpt')
    if os.path.isdir(wpt_default):
        return wpt_default

    return ''


def remove_shim() -> bool:
    """Deletes the .cmd shim from the wpt bin directory."""
    wpt_dir = get_wpt_bin_dir()
    if not wpt_dir:
        return True

    shim_path = os.path.join(wpt_dir, SHIM_NAME)
    if os.path.exists(shim_path):
        try:
            os.remove(shim_path)
            print(f"Successfully removed shim '{SHIM_NAME}' from {wpt_dir}.")
        except Exception as e:
            print(f'Warning: Failed to delete shim at {shim_path}: {e}', file=sys.stderr)
            return False
    return True


def remove_service():
    """Stops and removes the NSSM service or scheduled task."""
    if shutil.which('nssm'):
        print('Using NSSM to remove the service...')
        subprocess.run(['nssm', 'stop', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            ['nssm', 'remove', SERVICE_NAME, 'confirm'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print('Service removed.')
    else:
        print('Attempting to remove scheduled task...')
        cmd = f'schtasks /delete /tn "{SERVICE_NAME}" /f'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    # 1. Remove Service
    remove_service()

    # 2. Remove registry keys
    success = remove_from_registry(EXE_NAME)

    # 3. Remove CLI shim
    remove_shim()

    # 4. Clean up Program Files directory
    program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    target_install_dir = os.path.join(program_files, 'migasfree-agent')
    if os.path.isdir(target_install_dir):
        try:
            shutil.rmtree(target_install_dir)
            print(f"Successfully removed '{target_install_dir}'.")
        except Exception as e:
            print(f'Warning: Failed to delete directory {target_install_dir}: {e}', file=sys.stderr)

    if not success:
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
