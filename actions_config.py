# Define actions for GIT resources
def git_clone(name, param):
    import os
    print(f"Cloning {self.url} on branch {branch}")
    os.system(f'git clone -b {branch} {self.url}')


def git_pull(self):
    import subprocess
    print(f"Pulling from {self.url}")
    subprocess.run(['git', 'pull'], check=True)

# Define actions for SVN resources


def svn_checkout(self, branch="trunk"):
    import os
    print(f"Checking out {self.url} on branch {branch}")
    os.system(f'svn checkout {self.url}/branches/{branch}')


def svn_update(self):
    import subprocess
    print(f"Updating the repository from {self.url}")
    subprocess.run(['svn', 'update'], check=True)


# Map actions to resource types
ACTIONS = {
    "GIT": {
        "clone": git_clone,
        "pull": git_pull,
    },
    "SVN": {
        "checkout": svn_checkout,
        "update": svn_update,
    },
    "ELEMENT": {
        "open": (lambda: None),
    }
}
