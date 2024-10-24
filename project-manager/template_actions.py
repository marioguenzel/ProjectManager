import os


# == Define actions for resources ==
def git_clone(dir, name, type, pname, param):
    os.system(f"git clone {param['source']} '{param['folder']}'")


def git_pull(dir, name, type, pname, param):
    os.system(f"git -C '{param['folder']}' pull")


def svn_checkout(dir, name, type, pname, param):
    os.system(f"svn checkout {param['source']} '{param['folder']}'")


def svn_update(dir, name, type, pname, param):
    os.system(f"svn update '{param['folder']}'")


def remove(dir, name, type, pname, param):
    if input(f"Remove {param['folder']}? (y=yes)") != 'y':
        return
    os.system(f"rm -rf '{param['folder']}'")


def vscode(dir, name, type, pname, param):
    os.system(f"code '{param['folder']}'")


def open_link(dir, name, type, pname, param):
    os.system(f"open '{param['source']}'")


def iterm_folder(dir, name, type, pname, param):
    os.system(f"open -a iterm '{param['folder']}'")


def show_channel_element(dir, name, type, pname, param):
    os.system(
        fr"open -a element element://vector/webapp/#/room/\!{param['source']}")


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
        "show room": show_channel_element,
    },
    "LINK": {
        "open link": open_link,
    }
}
