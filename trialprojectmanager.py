#!/usr/bin/env python3.12
import yaml
import os

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import Application


# Specify the path to the projects.yaml file
PROJECTS_FILE = os.path.expanduser('~/Documents/MySVN/projects.yaml')

# Specify paths for GIT and SVN
GITFOLDER = os.path.expanduser('~/ProjectManager/GIT')
SVNFOLDER = os.path.expanduser('~/ProjectManager/SVN')


# === Resources ===

class Resource:
    actions = []
    def __init__(self, name, type, **args):
        self.name = name
        self.type = type

    def string(self):
        return f'{self.type}: {self.name}'

    def make_action(self, index):
        pass

class ResourceLink(Resource):
    type = 'LINK'
    actions = ['open link']
    def __init__(self, name, source, type=None, project=None):
        self.name = name
        self.source = source
    
    def make_action(self, action):
        if action == 0:
            # open link
            os.system(f"open '{self.source}'")
        else: 
            raise ValueError(f'{action=} out of range.')

class ResourceGit(Resource):
    type = 'GIT'
    actions = ['code', 'iterm', 'git clone']
    def __init__(self, name, source=None, folder=None, type=None, project=None):
        self.name = name
        self.source = source
        if folder is not None:
            self.folder = folder
        else:
            self.folder = os.path.join(GITFOLDER, project.name + '_' + self.name)
    
    def make_action(self, index):
        if self.actions[index] == 'code':
            # code
            os.system(f"code '{self.folder}'")
        elif self.actions[index] == 'iterm':
            # iterm 
            os.system(f"open -a iterm {self.folder}")
        elif self.actions[index] == 'git clone':
            # git clone
            if self.source is not None:
                os.system(f"git clone {self.source} '{self.folder}'")
        else: 
            raise ValueError(f'{self.actions[index]=} undefined.')

class ResourceSvn(Resource):
    type = 'SVN'
    actions = ['code', 'iterm', 'svn checkout']
    def __init__(self, name, source=None, folder=None, type=None, project=None):
        self.name = name
        self.source = source

        if folder is not None:
            self.folder = folder
        else:
            self.folder = os.path.join(GITFOLDER, project.name + '_' + self.name)
    
    def make_action(self, index):
        if self.actions[index] == 'code':
            # code
            os.system(f"code '{self.folder}'")
        elif self.actions[index] == 'iterm':
            # iterm 
            os.system(f"open -a iterm {self.folder}")
        elif self.actions[index] == 'svn checkout':
            # svn checkout
            if self.source is not None:
                os.system(f"svn checkout {self.source} '{self.folder}'")
        else: 
            raise ValueError(f'{self.actions[index]=} undefined.')

class ResourceElement(Resource):
    type = 'ELEMENT'
    actions = ['show channel']
    def __init__(self, name, source, folder=None, type=None, project=None):
        self.name = name
        self.source = source
    
    def make_action(self, index):
        if self.actions[index] == 'show channel':
            os.system(fr"open -a element element://vector/webapp/#/room/\!{self.source}")
        else: 
            raise ValueError(f'{self.actions[index]=} undefined.')

class ResourceFile(Resource):
    type = 'FILE'
    actions = ['iterm folder', 'code file']
    def __init__(self, name, folder=None, filename='', type=None, project=None):
        self.name = name
        self.filename = filename
        if folder is not None:
            self.folder = folder
        else:
            self.folder = os.path.join(GITFOLDER, project.name + '_' + self.name)
    
    def make_action(self, index):
        if self.actions[index] == 'iterm folder':
            os.system(f"open -a iterm {self.folder}")
        elif self.actions[index] == 'code file':
            os.system(f"code {os.path.join(self.folder,self.filename)}")
        else: 
            raise ValueError(f'{self.actions[index]=} undefined.')



class Project:
    def __init__(self, name, tags=[], resources=[]):
        self.name = name
        self.tags = tags
        self.resources = []
        for res in resources:
            if res['type'] == 'LINK':
                self.resources.append(ResourceLink(project=self, **res))
            elif res['type'] == 'GIT':
                self.resources.append(ResourceGit(project=self, **res))
            elif res['type'] == 'SVN':
                self.resources.append(ResourceSvn(project=self, **res))
            elif res['type'] == 'ELEMENT':
                self.resources.append(ResourceElement(project=self, **res))
            elif res['type'] == 'FILE':
                self.resources.append(ResourceFile(project=self, **res))
            else:
                raise ValueError(f'Unknown resource type: {res['type']}')

    def string(self):
        return f'{self.name}'



# === Prompt Toolkit ===

from prompt_toolkit import Application
from prompt_toolkit.layout.containers import VSplit, Window,HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.completion import WordCompleter


def listtext(somelist, index=None):
    printlist = []
    for idx, entry in enumerate(somelist):
        if type(entry) == str:
            entrystr = entry
        else: 
            entrystr = entry.string()
        if idx == index:
            printlist.append('> ' + entrystr)
        else:
            printlist.append('  ' + entrystr)
    text='\n'.join(printlist)
    return text
    
class WindowManager:
    def __init__(self, projects: list[Project] = []):
        self.projects_window = Window(content=FormattedTextControl(),always_hide_cursor=True)
        self.resource_window = Window(content=FormattedTextControl(),always_hide_cursor=True)
        self.actions_window = Window(content=FormattedTextControl(),always_hide_cursor=True)

        self.projects = projects
        self.focus_index = 0
        self.choice_index = [0, 0, 0]
    

    def update_windows(self):
        if self.focus_index == 0:
            self.projects_window.content.text = listtext(self.projects,self.choice_index[0])
            self.resource_window.content.text = listtext(self.projects[self.choice_index[0]].resources, None)
            self.actions_window.content.text = ''
        elif self.focus_index == 1:
            self.projects_window.content.text = listtext(self.projects,self.choice_index[0])
            self.resource_window.content.text = listtext(self.projects[self.choice_index[0]].resources,self.choice_index[1])
            self.actions_window.content.text = listtext(self.projects[self.choice_index[0]].resources[self.choice_index[1]].actions, None)
        elif self.focus_index == 2:
            self.projects_window.content.text = listtext(self.projects,self.choice_index[0])
            self.resource_window.content.text = listtext(self.projects[self.choice_index[0]].resources,self.choice_index[1])
            self.actions_window.content.text = listtext(self.projects[self.choice_index[0]].resources[self.choice_index[1]].actions, self.choice_index[2])
        else:
            raise ValueError(f'{self.focus_index=} out of range')
    
    def make_choice(self):
        if self.focus_index == 0:
            self.focus_index += 1
        elif self.focus_index == 1:
            self.focus_index += 1
        elif self.focus_index == 2:
            self.make_action()
    
    def revert_choice(self):
        if self.focus_index == 0:
            pass
        elif self.focus_index == 1:
            self.focus_index -= 1
            self.choice_index[1] = 0
        elif self.focus_index == 2:
            self.focus_index -= 1
            self.choice_index[2] = 0
    
    def up(self):
        lower_range = 0
        if self.choice_index[self.focus_index] > lower_range:
            self.choice_index[self.focus_index] -= 1 

    def down(self):
        if self.focus_index == 0:
            upper_range = len(self.projects)-1
        elif self.focus_index == 1:
            upper_range = len(self.projects[self.choice_index[0]].resources) - 1
        elif self.focus_index == 2:
            upper_range = len(self.projects[self.choice_index[0]].resources[self.choice_index[1]].actions) - 1
        else: 
            raise ValueError(f'{self.focus_index=} out of bound.')
        if self.choice_index[self.focus_index] < upper_range:
            self.choice_index[self.focus_index] += 1
            
    
    def make_action(self):
        self.projects[self.choice_index[0]].resources[self.choice_index[1]].make_action(self.choice_index[2])
    
if __name__=='__main__':
    with open(PROJECTS_FILE, 'r') as file:
        data = yaml.safe_load(file)
        projects = [Project(entry, data[entry].get('tags',[]), data[entry].get('resources',[])) for entry in data.keys()]
    
    manager = WindowManager(projects)
    manager.update_windows()


    kb=KeyBindings()
    @kb.add('c-c')
    def _exit(event):
        """Exit"""
        event.app.exit()

    @kb.add('enter')
    def _enter(event):
        """Make a choice"""
        manager.make_choice()
        manager.update_windows()
    
    @kb.add('right')
    def _right(event):
        """Make a choice"""
        manager.make_choice()
        manager.update_windows()
    
    @kb.add('left')
    def _left(event):
        """Undo a choice"""
        manager.revert_choice()
        manager.update_windows()
    
    @kb.add('up')
    def _up(event):
        """Undo a choice"""
        manager.up()
        manager.update_windows()
    
    @kb.add('down')
    def _down(event):
        """Undo a choice"""
        manager.down()
        manager.update_windows()

    root_container = VSplit([manager.projects_window, manager.resource_window, manager.actions_window])
    app = Application(layout=Layout(root_container), full_screen=True, key_bindings=kb)
    app.run()

