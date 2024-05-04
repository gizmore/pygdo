import os.path
import subprocess
import tomlkit

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Util import Files

# Multi Providers are treated in a special way... :(
# You have to define them manually here.
MULTI_PROVIDERS = {
    'captcha': (['https://github.com/gizmore/pygdo-captcha', 'https://github.com/gizmore/pygdo-recaptcha'], ['ui']),
}


def git_remote_url(url: str, ssh: bool):
    if ssh:
        return url.replace('https://', 'ssh://git@')
    else:
        return url.replace('ssh://git@', 'https://')


def get_git_remote(path, ssh: bool = False):
    try:
        cmd = ['git', '-C', path, 'config', '--get', 'remote.origin.url']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        origin_remote = result.stdout.strip()
        return git_remote_url(origin_remote, False)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        return None


def create_providers():
    global MULTI_PROVIDERS
    Application.init(os.path.dirname(__file__))
    loader = ModuleLoader.instance()
    modules = loader.load_modules_fs()
    data = {}
    for module in modules.values():
        if module.is_installable():
            data[module.get_name()] = [
                [get_git_remote(module.file_path())],
                module.gdo_dependencies(),
                module.gdo_is_site_module(),
            ]
    # Overwrite with multi providers.
    for name, value in MULTI_PROVIDERS.items():
        data[name] = [value[0], value[1]]
    file_contents = tomlkit.dumps(dict(sorted(data.items())))
    print("------------ PROVIDERS -----------")
    print(file_contents)
    print("----------------------------------")
    Files.put_contents(Application.file_path('gdo/base/res/deps.toml'), file_contents)


if __name__ == "__main__":
    create_providers()
