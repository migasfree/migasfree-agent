import os
import shutil
import subprocess
import sys

# Windows HKLM App Paths key location
APP_PATHS_BASE = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths'
EXE_NAME = 'migasfree-agent.exe'
SHIM_NAME = 'migasfree-agent.cmd'
SERVICE_NAME = 'migasfree-agent'


def register_in_app_paths(exe_path: str, install_dir: str) -> bool:
    """Registers the executable in Windows App Paths for global shell execution."""
    if sys.platform != 'win32':
        return True

    import winreg

    app_paths_key = f'{APP_PATHS_BASE}\\{EXE_NAME}'
    try:
        with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, app_paths_key) as key:
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, exe_path)
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_SZ, install_dir)
        print(f"Successfully registered '{EXE_NAME}' in Windows App Paths.")
    except Exception as e:
        print(f'Error writing Registry App Paths: {e}', file=sys.stderr)
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


def create_shim(exe_path: str) -> bool:
    """Creates a .cmd shim in the wpt bin directory if possible."""
    wpt_dir = get_wpt_bin_dir()
    if not wpt_dir:
        print('Warning: Could not locate wpt installation directory. Shim was not created.')
        return True

    shim_path = os.path.join(wpt_dir, SHIM_NAME)
    try:
        shim_content = f'@echo off\n"{exe_path}" %*\n'
        with open(shim_path, 'w', encoding='utf-8') as f:
            f.write(shim_content)
        print(f"Successfully created shim '{SHIM_NAME}' at {shim_path}.")
        return True
    except Exception as e:
        print(f'Warning: Failed to create shim at {shim_path}: {e}', file=sys.stderr)
        return False


def update_pkg_list(target_dir: str) -> None:
    """Regenerate the WPT .list manifest with actual installed paths."""
    pkg_list = os.environ.get('WPT_PKG_LIST')
    if not pkg_list:
        return

    files = []
    for root, _, archives in os.walk(target_dir):
        for item in archives:
            files.append(os.path.join(root, item))

    with open(pkg_list, 'w', encoding='utf-8') as f:
        for path in sorted(files):
            f.write(f'{path}\n')


def configure_service(exe_path: str, install_dir: str):
    """Configures the agent to run as a Windows service using NSSM or schtasks."""
    if shutil.which('nssm'):
        print('Using NSSM to configure the service...')
        subprocess.run(['nssm', 'stop', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            ['nssm', 'remove', SERVICE_NAME, 'confirm'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        try:
            subprocess.run(['nssm', 'install', SERVICE_NAME, exe_path], check=True)
            subprocess.run(['nssm', 'set', SERVICE_NAME, 'AppDirectory', install_dir], check=True)
            subprocess.run(['nssm', 'set', SERVICE_NAME, 'DisplayName', 'Migasfree Agent'], check=True)
            subprocess.run(
                ['nssm', 'set', SERVICE_NAME, 'Description', 'Multi-protocol TCP tunnel agent for remote access'],
                check=True,
            )
            subprocess.run(['nssm', 'set', SERVICE_NAME, 'Start', 'SERVICE_AUTO_START'], check=True)
            subprocess.run(
                ['nssm', 'set', SERVICE_NAME, 'AppStdout', os.path.join(install_dir, 'agent.log')], check=True
            )
            subprocess.run(
                ['nssm', 'set', SERVICE_NAME, 'AppStderr', os.path.join(install_dir, 'agent.log')], check=True
            )
            subprocess.run(['nssm', 'set', SERVICE_NAME, 'AppRotateFiles', '1'], check=True)
            subprocess.run(['nssm', 'set', SERVICE_NAME, 'AppRotateBytes', '1048576'], check=True)

            print('Starting Migasfree Agent service...')
            subprocess.run(['nssm', 'start', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print('Service created and started successfully.')
        except subprocess.CalledProcessError as e:
            print(f'Error configuring NSSM service: {e}', file=sys.stderr)
    else:
        print('NSSM not found. Creating scheduled task instead...')
        cmd = f'schtasks /create /tn "{SERVICE_NAME}" /tr "\\"{exe_path}\\"" /sc onstart /ru SYSTEM /f'
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(
            f'schtasks /run /tn "{SERVICE_NAME}"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )


def stop_service():
    """Stops the service if it exists to unlock files for replacement/deletion."""
    if sys.platform != 'win32':
        return

    if shutil.which('nssm'):
        subprocess.run(['nssm', 'stop', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(['sc', 'stop', SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    # Stop the running service (if any) to prevent file locks
    stop_service()

    # 1. Paths resolution
    wpt_install_dir = os.environ.get('WPT_INSTALL_DIR')
    if not wpt_install_dir:
        print('Error: WPT_INSTALL_DIR is not set.', file=sys.stderr)
        sys.exit(1)

    program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
    target_install_dir = os.path.join(program_files, 'migasfree-agent')
    target_exe_path = os.path.join(target_install_dir, EXE_NAME)

    print(f"[*] Relocating migasfree-agent files to '{target_install_dir}'...")

    try:
        if os.path.exists(target_install_dir):
            shutil.rmtree(target_install_dir)

        shutil.copytree(wpt_install_dir, target_install_dir)

        for item in os.listdir(wpt_install_dir):
            item_path = os.path.join(wpt_install_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

        print('[+] Files successfully relocated and managed cache cleared.')
    except Exception as e:
        print(f'Error relocating files: {e}', file=sys.stderr)
        sys.exit(1)

    # Update the WPT .list manifest with the actual installed paths
    update_pkg_list(target_install_dir)

    # 2. Register in App Paths
    success = register_in_app_paths(target_exe_path, target_install_dir)
    if not success:
        sys.exit(1)

    # 3. Create CLI shim
    create_shim(target_exe_path)

    # 4. Configure Service
    configure_service(target_exe_path, target_install_dir)

    print('migasfree-agent installation completed successfully.')
    sys.exit(0)


if __name__ == '__main__':
    main()
