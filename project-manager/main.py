#!/usr/bin/env python3.12
import shutil
from prompt_toolkit.layout.containers import VSplit, Window, HSplit
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
import yaml
import os
import sys
import argparse
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import Application


# === Resources and Projects ===

LOCATION = '.'
ACTIONS = dict()


class Resource:
    def __init__(self, name, type, project=None, **kwargs):
        self.name = name
        self.type = type
        self.param = kwargs
        self.project = project

    def string(self):
        if self.type == 'GIT' or self.type == 'SVN':
            try:
                if not os.path.exists(os.path.join(LOCATION, self.type, self.project.name, self.name)):
                    return f'({self.type}: {self.name})'
            except:
                pass
        return f'{self.type}: {self.name}'

    def make_action(self, action_id, directory=None):
        list(ACTIONS[self.type].values())[action_id](
            directory, self.name, self.type, self.project.name, self.param)


class Project:
    def __init__(self, name, tags=[], resources=[]):
        self.name = name
        self.tags = tags
        self.resources = []
        for res in resources:
            self.resources.append(
                Resource(project=self, name=res, **resources[res]))

    def string(self):
        return f'{self.name} {self.tags}'


# === Prompt Toolkit ===
def listtext(somelist, index=None, active=True):
    printlist = []
    for idx, entry in enumerate(somelist):
        if type(entry) == str:
            entrystr = entry
        else:
            entrystr = entry.string()

        if idx == index and active is True:
            printlist.append('> ' + entrystr)
        elif idx == index and active is False:
            printlist.append('- ' + entrystr)
        else:
            printlist.append('  ' + entrystr)
    text = '\n'.join(printlist)
    return text


class WindowManager:
    def __init__(self, projects: list[Project] = []):
        self.projects_window = Window(
            content=FormattedTextControl(), always_hide_cursor=True, ignore_content_width=True)
        self.resource_window = Window(
            content=FormattedTextControl(), always_hide_cursor=True, ignore_content_width=True)

        self.top_window = Window(
            content=FormattedTextControl(), height=1, always_hide_cursor=True)
        self.bottom_window = None  # TODO: Bottom text

        self.projects = projects
        self.filters = []
        self.focus_index = 0
        self.choice_index = [0, 0]

        self.action = None

    def update_windows(self):
        self.top_window.content.text = 'h = help,    applied filters = ' + \
            str(self.filters)
        if self.focus_index == 0:
            self.projects_window.content.text = listtext(
                self.projects, self.choice_index[0])
            self.resource_window.content.text = listtext(
                self.projects[self.choice_index[0]].resources, None)
        elif self.focus_index == 1:
            self.projects_window.content.text = listtext(
                self.projects, self.choice_index[0], active=False)
            self.resource_window.content.text = listtext(
                self.projects[self.choice_index[0]].resources, self.choice_index[1])
        else:
            raise ValueError(f'{self.focus_index=} out of range')

    def up(self):
        lower_range = 0
        if self.choice_index[self.focus_index] > lower_range:
            self.choice_index[self.focus_index] -= 1

    def down(self):
        if self.focus_index == 0:
            upper_range = len(self.projects)-1
        elif self.focus_index == 1:
            upper_range = len(
                self.projects[self.choice_index[0]].resources) - 1
        else:
            raise ValueError(f'{self.focus_index=} out of bound.')

        if self.choice_index[self.focus_index] < upper_range:
            self.choice_index[self.focus_index] += 1

    def filter(self):
        filter = prompt('Enter a filter: ',
                        completer=WordCompleter(self.get_tags()))
        self.projects = [proj for proj in self.projects if filter in proj.tags]
        self.filters.append(filter)
        self.focus_index = 0
        self.choice_index = [0, 0]

    def get_tags(self):
        tags = list(set(tag for proj in self.projects for tag in proj.tags))
        tags.sort()
        return tags

    def make_action(self, index):
        self.projects[self.choice_index[0]
                      ].resources[self.choice_index[1]].make_action(index, directory=LOCATION)

    def choose_action(self):
        current_resource = self.projects[self.choice_index[0]
                                         ].resources[self.choice_index[1]]
        action_name = prompt(f'Choose an action for {current_resource.string()}: ',
                             completer=WordCompleter(ACTIONS[current_resource.type]))
        if action_name in ACTIONS[current_resource.type].keys():
            self.make_action(
                list(ACTIONS[current_resource.type].keys()).index(action_name))

    def keybindings(self):
        # Specify keybindings
        kb = KeyBindings()  # TODO: different keybindings for left and right window

        @kb.add('c-c')
        @kb.add('q')
        def _exit(event):
            """Exit"""
            self.action = 'quit'
            event.app.exit()

        @kb.add('right')
        @kb.add('enter')
        def _enter(event):
            """Right/Make a choice"""
            if self.focus_index == 0:
                self.focus_index = 1
                self.update_windows()
            else:
                self.action = 'enter'
                event.app.exit()

        @kb.add('left')
        def _left(event):
            """Left"""
            if self.focus_index == 1:
                self.focus_index -= 1
                self.choice_index[1] = 0
            else:
                pass
            self.update_windows()

        @kb.add('up')
        def _up(event):
            """Up"""
            self.up()
            self.update_windows()

        @kb.add('down')
        def _down(event):
            """Down"""
            self.down()
            self.update_windows()

        @kb.add('f')
        def _filter(event):
            """Filter"""
            self.action = 'filter'
            event.app.exit()

        @kb.add('r')
        def _reset(event):
            """Refresh"""
            self.action = 'refresh'
            event.app.exit()

        @kb.add('a')
        def _choose_action(event):
            """Choose an action from list"""
            if self.focus_index == 1:
                self.action = 'choose action'
                event.app.exit()

        @kb.add('i')
        def _choose_action(event):
            """Show information for a resource/project."""
            self.action = 'info'
            event.app.exit()

        @kb.add('h')
        def _help(event):
            """Help for keybindings"""
            self.action = 'help'
            event.app.exit()

        return kb


def main():
    global LOCATION
    global ACTIONS

    parser = argparse.ArgumentParser(prog='python -m project-manager')

    parser.add_argument('LOCATION', type=Path,
                        help='Specify folder.')
    parser.add_argument('-i', '--init', action='store_true',
                        help='Initialilze a new project folder.')
    parser.add_argument('-a', '--all', nargs=2, metavar=('TYPE', 'ACTION'),
                        help='Apply an action to all resources of a type.')

    args = parser.parse_args()

    LOCATION = args.LOCATION.resolve()

    if args.init:
        # Get the directory where the script (Python file) is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        for source, destination in [('template_actions.py', 'actions.py'), ('template_projects.yaml', 'projects.yaml')]:

            source_file = os.path.join(script_dir, source)
            destination_file = os.path.join(LOCATION, destination)

            if os.path.exists(destination):
                if input(f'Overwrite {destination}? (y=yes)') != 'y':
                    break

            # Copy the file
            try:
                shutil.copy(source_file, destination_file)
            except FileNotFoundError:
                print(f"File {source} not found in the script's directory.")

    elif args.all is not None:
        # Config
        sys.path.insert(0, str(LOCATION))
        from actions import ACTIONS

        with open(os.path.join(LOCATION, 'projects.yaml'), 'r') as file:
            data = yaml.safe_load(file)
            projects = [Project(entry, data[entry].get('tags', []), data[entry].get(
                'resources', [])) for entry in data.keys()]

        # Do actions:
        assert args.all[0] in ACTIONS
        assert args.all[1] in ACTIONS[args.all[0]]

        action_id = list(ACTIONS[args.all[0]]).index(args.all[1])

        for proj in projects:
            for res in proj.resources:
                if res.type == args.all[0]:
                    res.make_action(action_id, directory=LOCATION)

    else:
        # Config
        sys.path.insert(0, str(LOCATION))
        from actions import ACTIONS

        while True:
            with open(os.path.join(LOCATION, 'projects.yaml'), 'r') as file:
                data = yaml.safe_load(file)
                projects = [Project(entry, data[entry].get('tags', []), data[entry].get(
                    'resources', [])) for entry in data.keys()]

            manager = WindowManager(projects)
            manager.update_windows()

            kb = manager.keybindings()

            root_container = HSplit([manager.top_window, VSplit(
                [manager.projects_window, manager.resource_window])])
            app = Application(layout=Layout(root_container),
                              full_screen=True, key_bindings=kb)

            while True:
                # update windows and run
                manager.update_windows()
                app.run()

                # Check action
                if manager.action == 'quit':
                    quit()
                elif manager.action == 'filter':
                    manager.filter()
                elif manager.action == 'refresh':
                    break
                elif manager.action == 'enter':
                    manager.make_action(0)
                elif manager.action == 'choose action':
                    manager.choose_action()
                elif manager.action == 'help':
                    print("\n=== Help - Key Bindings Overview===")
                    for binding in kb.bindings:
                        keys = ", ".join([str(key) for key in binding.keys])
                        keyentry = binding.handler.__doc__.strip(
                        ) if binding.handler.__doc__ else 'No description'
                        if keys == 'Keys.ControlC':
                            keys = 'control-c'
                        elif keys == 'Keys.ControlM':
                            keys = 'enter'
                        elif keys == 'Keys.Right':
                            keys = 'right'
                        elif keys == 'Keys.Left':
                            keys = 'left'
                        elif keys == 'Keys.Up':
                            keys = 'up'
                        elif keys == 'Keys.Down':
                            keys = 'down'
                        print(f"\t{keys} - {keyentry}")
                    input('Press enter to go back ...')
                elif manager.action == 'info':
                    current_project = manager.projects[manager.choice_index[0]]
                    current_resource = current_project.resources[manager.choice_index[1]]
                    if manager.focus_index == 0:
                        print("\n=== Info for project ===")
                        print(f'Name: {current_project.name}')
                        print(f'Tags: {current_project.tags}')
                        print('Resources: ')
                        [print('- ' + res.string())
                         for res in current_project.resources]
                        print('======')
                    elif manager.focus_index == 1:
                        print("\n=== Info for resource ===")
                        print('In project:' + current_resource.project.string())
                        print(f'Name: {current_resource.name}')
                        print(f'Type: {current_resource.type}')
                        print(f'Parameters: {current_resource.param}')
                        print('======')
                    input('Press enter to go back ...')

                # Reset action
                manager.action = None


if __name__ == "__main__":
    main()
