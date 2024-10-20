from setuptools import setup, find_packages


def load_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='project-manager',  # Replace with your package name
    version='0.1.0',  # Version of your package
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=load_requirements(),  # List any dependencies here
    include_package_data=True,  # This is important to include non-code files.
    package_data={
        'project-manager': ['template_projects.yaml'],
    },
    description='A simple project manager for resources like GIT, SVN, LINKS, etc.',
    author='Mario Guenzel',
    url='https://github.com/marioguenzel/ProjectManager',
    python_requires=">=3.11",
)
