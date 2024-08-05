#!/usr/bin/env python3.12
import yaml
import os
import inquirer
import argparse

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import Application


# Specify the path to the projects.yaml file
PROJECTS_FILE = os.path.expanduser('~/Documents/MySVN/projects.yaml')

# Specify paths for GIT and SVN
GITFOLDER = os.path.expanduser('~/ProjectManager/GIT')
SVNFOLDER = os.path.expanduser('~/ProjectManager/SVN')

TYPES = ['LINK','GIT','SVN', 'ELEMENT', 'FILE']

ACTIONS = {'LINK': ['open link'], 
           'GIT': ['code', 'iterm', 'git clone'],
           'SVN': ['code', 'iterm', 'svn checkout'],
           'ELEMENT': ['show channel'],
           'FILE': ['iterm folder', 'code file']}


# INQUIRER:



def choose_project(data):
    projects = data.keys()
    questions = [
    inquirer.List('Project',
                        message="Choose a project:",
                        choices=projects,
                        ),
    ]
    answer = inquirer.prompt(questions)['Project']
    return answer

def choose_resource(data, project):
    resources = data[project]['resources']
    options = [f"{src['type']}: {src['name']}, {src.get('source','<No Resource>')}" for src in resources]
    questions = [
    inquirer.List('Resource',
                        message="Choose a resource:",
                        choices=options,
                        ),
    ]
    answer = inquirer.prompt(questions)['Resource']
    return options.index(answer)

def choose_action(data, project, resource_id):
    resource = data[project]['resources'][resource_id]
    available_actions = ACTIONS[resource['type']]
    questions = [
    inquirer.List('Action',
                        message="Choose an action:",
                        choices=available_actions,
                        ),
    ]
    answer = inquirer.prompt(questions)['Action']
    return answer

def make_folder(type,foldername):
    if type == 'GIT':
        return os.path.join(GITFOLDER,foldername)
    elif type == 'SVN':
        return os.path.join(SVNFOLDER,foldername)
    else:
        raise ValueError(f'{type=} not allowed in make_folder function.')

def make_action(data, project, resource_id, action):
    resource = data[project]['resources'][resource_id]

    # specify folder
    if resource['type'] in ['SVN', 'GIT']:
        if 'folder' in resource.keys():
            folder = resource['folder']
        else:
            folder = make_folder(resource['type'], project + '_' + resource['name'])

    if action in ['open link',]:
        os.system(f"open '{resource['source']}'")
    
    elif action in ['show channel',]:
        os.system(fr"open -a element element://vector/webapp/#/room/\!{resource['source']}")
    
    elif action in ['iterm folder',]:
        os.system(f"open -a iterm {resource['folder']}")
    
    elif action in ['code file',]:
        os.system(f"code {os.path.join(resource['folder'],resource['filename'])}")

    elif action in ['code',]:
        if os.path.exists(folder) is True:
            os.system(f"code '{folder}'")
        else:
            print('Folder does not exist.')
    
    elif action in ['git clone',]:
        if os.path.exists(folder) is True:
            print(f'Folder {folder} already exist.')
        else:
            os.system(f"git clone {resource['source']} '{folder}'")
    
    elif action in ['svn checkout',]:
        if os.path.exists(folder) is True:
            print(f'Folder {folder} already exist.')
        else:
            os.system(f"svn checkout {resource['source']} '{folder}'")
    
    elif action in ['iterm',]:
        if os.path.exists(folder) is True:
            os.system(f"open -a iterm '{folder}'")
        else:
            print('Folder does not exist.')

    else:
        raise ValueError(f'{action=} not found.')
    
    return 4



def comma_separated_list(value):
    return [x.strip() for x in value.split(',')]

def show_tags(data):
    projects_with_tags = [project for project in data.values() if 'tags' in project]
    tags = set(tag for project in projects_with_tags for tag in project['tags'])

    tags = list(tags)
    tags.sort()

    print("\n".join(tags))
    exit()

def filter_data(data,filtertags):
    new_data = {key: value for key, value in data.items() if all([tag in value.get('tags',[]) for tag in filtertags])}
    return new_data

def clone_all(data):
    for project in data.keys():
        for resource_id in range(len(data[project].get('resources',[]))):
            if data[project]['resources'][resource_id]['type'] == 'GIT':
                make_action(data,project,resource_id,'git clone')

def checkout_all(data):
    for project in data.keys():
        for resource_id in range(len(data[project].get('resources',[]))):
            if data[project]['resources'][resource_id]['type'] == 'SVN':
                make_action(data,project,resource_id,'svn checkout')


if __name__ == 'old__main__':

    # Open the file and load its contents using the yaml library
    with open(PROJECTS_FILE, 'r') as file:
        data = yaml.safe_load(file)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Manage your projects.")
    parser.add_argument('-f', '--filter', type=comma_separated_list, help='A comma-separated list of words to filter')
    parser.add_argument('--showtags', action='store_true', help='Show tags that are used in data.')
    parser.add_argument('--cloneall', action='store_true', help='Clone all GIT repos.')
    parser.add_argument('--checkoutall', action='store_true', help='Checkout all SVN repos.')
    parser.add_argument('-pf', '--projectsfile', action='store_true', help='Show location of the "projects.yaml" file.')
    args = parser.parse_args()

    if args.projectsfile:
        print(PROJECTS_FILE)
        exit()

    if args.filter is not None:
        data = filter_data(data, args.filter)

    if args.showtags:
        show_tags(data)
    
    if args.cloneall:
        clone_all(data)
    
    if args.checkoutall:
        checkout_all(data)
    
    if args.showtags or args.cloneall or args.checkoutall:
        exit()
    

    depth = 0
    project = None
    resource_id = None
    action = None

    for _ in range(3):

        if depth==0:
            project = choose_project(data)
            depth = 1

        if depth==1:
            resource_id = choose_resource(data,project)
            depth = 2

        if depth==2:
            action = choose_action(data,project,resource_id)
            depth=3
        
        if depth==3:
            depth = make_action(data, project, resource_id, action)
        
        if depth==4:
            exit()

        # if depth==3:
        #     make_action(data,project)



TYPES = ['LINK','GIT','SVN', 'ELEMENT', 'FILE']

ACTIONS = {'LINK': ['open link'], 
           'GIT': ['code', 'iterm', 'git clone'],
           'SVN': ['code', 'iterm', 'svn checkout'],
           'ELEMENT': ['show channel'],
           'FILE': ['iterm folder', 'code file']}

# Resources

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



from prompt_toolkit import Application
from prompt_toolkit.layout.containers import VSplit, Window,HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.completion import WordCompleter

class ChooseProject:
    def __init__(self,projects: list[Project]):
        self.all_projects = projects
        self.projects = projects
        self.index=0 # index of choice
        self.textcontrol = FormattedTextControl(text='Hello world')
        self.next_action = None
        self.filters = []
    
    def index_up(self):
        if self.index < len(self.projects)-1:
            self.index += 1

    def index_down(self):
        if self.index>0:
            self.index -= 1
    
    def filter(self, filter):
        self.filters.append(filter)
        self.projects = [proj for proj in self.projects if filter in proj.tags]
    
    def remove_filters(self):
        self.filters = []
        self.projects = self.all_projects[:]
    
    def get_tags(self):
        tags = list(set(tag for proj in self.projects for tag in proj.tags))
        tags.sort()
        return tags
    
    def make_list_container(self):
        printlist = []
        for idx, entry in enumerate(self.projects):
            if idx == self.index:
                printlist.append('> ' + entry.name)
            else:
                printlist.append('  ' + entry.name)
        self.textcontrol.text='\n'.join(printlist)

    def tui_choice(self):
        self.next_action = None

        kb=KeyBindings()
        @kb.add('c-c')
        def _exit(event):
            """Exit"""
            self.next_action = 'quit'
            event.app.exit()
        
        @kb.add('enter')
        def _enter(event):
            """Make a choice"""
            self.next_action = '+'
            event.app.exit()
        
        @kb.add('down')
        def _move_down(event):
            self.index_up()
            self.make_list_container()

        @kb.add('up')
        def _move_up(event):
            self.index_down()
            self.make_list_container()
        
        @kb.add('f')
        def _filter(event):
            self.next_action = 'filter'
            event.app.exit()
        
        @kb.add('r')
        def _remove_filter(event):
            self.remove_filters()
            self.next_action = None
            event.app.exit()
        
        while True:
            self.make_list_container()
            root_container = HSplit([Window(content=FormattedTextControl(text=f'f: filter, r: remove filters\ncurrent filters: {self.filters}'), always_hide_cursor=True, height=2),Window(content=self.textcontrol, always_hide_cursor=True)])
            layout = Layout(root_container)
            app = Application(layout=layout, full_screen=True, key_bindings=kb)
            app.run()

            if self.next_action is None:
                continue
            elif self.next_action == 'filter':
                # filter and repeat
                filter = prompt('Enter a filter: ', completer=WordCompleter(self.get_tags()))
                self.filter(filter)
                self.index = 0
                continue
            else:
                return self.next_action

class ChooseResource:
    pass


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




if False:
    with open(PROJECTS_FILE, 'r') as file:
        data = yaml.safe_load(file)
        projects = [Project(entry, data[entry].get('tags',[]), data[entry].get('resources',[])) for entry in data.keys()]

    resources = []

    focus_index = 0

    choice_index = [0,0,0]
    
    projects_window = Window(content=FormattedTextControl(text='test1'),always_hide_cursor=True)
    resource_window = Window(content=FormattedTextControl(text='test2'),always_hide_cursor=True)
    actions_window = Window(content=FormattedTextControl(text='test3'),always_hide_cursor=True)

    def update_windows():
        if focus_index == 0:
            projects_window.content.text = listtext(projects,choice_index[0])
            resource_window.content.text = ''
            actions_window.content.text = ''
        elif focus_index == 1:
            projects_window.content.text = listtext(projects,choice_index[0])
            resource_window.content.text = listtext(projects[choice_index[0]].resources,choice_index[1])
            actions_window.content.text = ''
        elif focus_index == 2:
            projects_window.content.text = listtext(projects,choice_index[0])
            resource_window.content.text = listtext(projects[choice_index[0]].resources,choice_index[1])
            actions_window.content.text = 'test'
        else:
            raise ValueError(f'{focus_index=} out of range')

    kb=KeyBindings()
    @kb.add('c-c')
    def _exit(event):
        """Exit"""
        event.app.exit()

    @kb.add('enter')
    def _enter(event):
        global focus_index
        """Make a choice"""
        if focus_index <2:
            focus_index +=1
            update_windows()
    
    @kb.add('right')
    def _right(event):
        global focus_index
        """Make a choice"""
        if focus_index <2:
            focus_index +=1
            update_windows()
    
    @kb.add('left')
    def _left(event):
        global focus_index
        """Undo a choice"""
        if focus_index >0:
            choice_index[focus_index] = 0
            focus_index -= 1
            update_windows()
    
    @kb.add('up')
    def _up(event):
        global choice_index
        """Undo a choice"""
        if choice_index[focus_index] >0:
            choice_index[focus_index] -= 1
            update_windows()
    
    @kb.add('down')
    def _down(event):
        global choice_index
        """Undo a choice"""
        if focus_index == 0:
            if choice_index[0] < len(projects)-1:
                choice_index[0] += 1
                update_windows()
        elif focus_index == 1:
            if choice_index[1] < len(projects[choice_index[0]].resources)-1:
                choice_index[1] += 1
                update_windows()
        elif focus_index == 2:
            if choice_index[2] < len(projects[choice_index[0]].resources[choice_index[1]])-1:
                choice_index[2] += 1
                update_windows()
        else:
            raise ValueError(f'{focus_index=} out of range.')


    update_windows()

    root_container = VSplit([projects_window, resource_window, actions_window])
    app = Application(layout=Layout(root_container), full_screen=True, key_bindings=kb)


    app.run()

    # root_container = HSplit([Window(content=FormattedTextControl(text=f'f: filter, r: remove filters\ncurrent filters: {self.filters}'), always_hide_cursor=True, height=2),Window(content=self.textcontrol, always_hide_cursor=True)])



if False:
    # testlist = ['eins', 'zwei', 'drei']

    with open(PROJECTS_FILE, 'r') as file:
        data = yaml.safe_load(file)
        projects = [Project(entry, data[entry].get('tags',[]), data[entry].get('resources',[])) for entry in data.keys()]


    ch_proj = ChooseProject(projects)

    while True:
        action = ch_proj.tui_choice()
        if action == 'quit':
            break
        elif action == '+':
            pass
        

    # print(str(proj.index) + proj.projects[proj.index].name)

    # kb=KeyBindings()

    # @kb.add('c-c')
    # def _(event):
    #     """Exit"""
    #     event.app.exit()

    # # app = Application(full_screen=True, key_bindings=bindings)
    # # app.run()

    # from prompt_toolkit import Application
    # from prompt_toolkit.buffer import Buffer
    # from prompt_toolkit.layout.containers import VSplit, Window
    # from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
    # from prompt_toolkit.layout.layout import Layout

    # # buffer1 = Buffer()  # Editable buffer.

    # testlist = ['eins', 'zwei', 'drei']
    # index = 0

    # @kb.add('up')
    # def move_up(event):
    #     global index
    #     if index > 0:
    #         index -= 1
    #     make_menu()

    # @kb.add('down')
    # def move_down(event):
    #     global index
    #     if index < len(testlist) - 1:
    #         index += 1
    #     make_menu()

    # format_text = FormattedTextControl()

    # def make_menu():
    #     printlist = []
    #     for idx, entry in enumerate(testlist):
    #         if idx == index:
    #             printlist.append('> ' + entry)
    #         else:
    #             printlist.append('  ' + entry)
    #     format_text.text = '\n'.join(printlist)
    
    # make_menu()

    # root_container = Window(content=testlist)

    # # root_container = Window(content=format_text, always_hide_cursor=True)
    
    # # VSplit([
    # #     # # One window that holds the BufferControl with the default buffer on
    # #     # # the left.
    # #     # Window(content=BufferControl(buffer=buffer1)),

    # #     # # A vertical line in the middle. We explicitly specify the width, to
    # #     # # make sure that the layout engine will not try to divide the whole
    # #     # # width by three for all these windows. The window will simply fill its
    # #     # # content by repeating this character.
    # #     # Window(width=1, char='|'),

    # #     # Display the text 'Hello world' on the right.
    # #     Window(content=format_text),
    # # ])

    # layout = Layout(root_container)

    