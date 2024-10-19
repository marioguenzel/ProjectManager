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
from prompt_toolkit.shortcuts import radiolist_dialog


# === Resources and Projects ===

class Resource:
    def __init__(self, name, type, project=None, **kwargs):
        self.name = name
        self.type = type
        self.param = kwargs
        self.project = project

    def string(self):  # TODO in brackets if not downloaded yet
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
        return f'{self.name}'


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

        self.top_window = None  # TODO: Top text
        self.bottom_window = None  # TODO: Bottom text

        self.projects = projects
        self.focus_index = 0
        self.choice_index = [0, 0]

        self.action = None

    def update_windows(self):
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
        type = self.projects[self.choice_index[0]
                             ].resources[self.choice_index[1]].type
        result = radiolist_dialog(
            values=enumerate(ACTIONS[type]),
            title="Radiolist dialog example",
            text="Please select a color:",
        ).run()

    def keybindings(self):
        # Specify keybindings
        kb = KeyBindings()  # TODO: different keybindings for left and right window

        @kb.add('c-c')
        def _exit(event):
            """Exit"""
            self.action = 'quit'
            event.app.exit()

        @kb.add('enter')
        def _enter(event):
            """Make a choice"""
            if self.focus_index == 0:
                self.focus_index = 1
                self.update_windows()
            else:
                self.action = 'enter'
                event.app.exit()

        @kb.add('right')
        def _right(event):
            """Make a choice"""
            if self.focus_index == 0:
                self.focus_index = 1
                self.update_windows()
            else:
                self.action = 'enter'
                event.app.exit()

        @kb.add('left')
        def _left(event):
            """Undo a choice"""
            if self.focus_index == 1:
                self.focus_index -= 1
            else:
                pass
            self.update_windows()

        @kb.add('up')
        def _up(event):
            """Undo a choice"""
            self.up()
            self.update_windows()

        @kb.add('down')
        def _down(event):
            """Undo a choice"""
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
            self.action = 'choose action'
            event.app.exit()

        # TODO: i for info

        # TODO: h for help

        # TODO: q for quit

        # TODO: a for choose action

        # TODO: Show projects-folder

        return kb


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('LOCATION', type=Path,
                        help='Specify folder.')
    parser.add_argument('-i', '--init', action='store_true',
                        help='Initialilze a new project folder.')

    args = parser.parse_args()

    LOCATION = args.LOCATION.resolve()

    if args.init:
        # Get the directory where the script (Python file) is located
        script_dir = os.path.dirname(os.path.abspath(__file__))

        for source, destination in [('template_actions.py', 'actions.py'), ('template_projects.yaml', 'projects.yaml')]:

            source_file = os.path.join(script_dir, source)
            destination_file = os.path.join(LOCATION, destination)

            # Copy the file
            try:
                shutil.copy(source_file, destination_file)
            except FileNotFoundError:
                print(f"File {source} not found in the script's directory.")

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

            root_container = VSplit(
                [manager.projects_window, manager.resource_window])
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

                # Reset action
                manager.action = None

    # TODO: In Resource window: enter = standard action, a or shift+enter for choosing from list of actions (+ allow no action)
    # TODO: new format for resources:
    # resources:
    #     Paper:
    #         type: GIT
    #         source: ...
    #     Notes:
    #         type: LINK
    #         source: ...

    # TODO: Show tags behind project name
    # TODO: i: resource info
