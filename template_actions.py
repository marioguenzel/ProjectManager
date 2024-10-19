import os


# == Define actions for resources ==
def git_clone(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"git clone {param['source']} '{path}'")


def git_pull(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"git pull '{path}'")


def svn_checkout(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"svn checkout {param['source']} '{path}'")


def svn_update(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"svn update '{path}'")


def remove(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"rm -rf '{path}'")


def vscode(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"code '{path}'")


def open_link(dir, name, type, pname, param):
    os.system(f"open '{param['source']}'")


def iterm_folder(dir, name, type, pname, param):
    path = os.path.join(dir, type, pname, name)
    os.system(f"open -a iterm '{path}'")


# Map actions to resource types (top=default)
ACTIONS = {
    "GIT": {
        "code": vscode,
        "iterm folder": iterm_folder,
        "pull": git_pull,
        "clone": git_clone,
        "remove": remove,
    },
    "SVN": {
        "code": vscode,
        "iterm folder": iterm_folder,
        "update": svn_update,
        "checkout": svn_checkout,
        "remove": remove,
    },
    "ELEMENT": {
        "show room": open_link,
    },
    "LINK": {
        "open link": open_link,
    }
}
