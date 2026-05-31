import re

from cx_Freeze import Executable, setup


def get_version():
    with open('pyproject.toml', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return '1.3.0'


build_exe_options = {
    'packages': ['os', 'sys', 'asyncio', 'websockets', 'requests', 'migasfree_agent'],
    'excludes': ['tkinter', 'unittest', 'pydoc'],
}

setup(
    name='migasfree-agent',
    version=get_version(),
    description='Migasfree Agent',
    options={
        'build_exe': build_exe_options,
    },
    executables=[
        Executable(
            'migasfree_agent/agent.py',
            target_name='migasfree-agent.exe',
            base='Console',
        )
    ],
)
