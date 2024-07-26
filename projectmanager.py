import yaml
import os
import inquirer
import argparse

# Specify the path to the projects.yaml file
file_path = 'projects.yaml'

GITFOLDER = os.path.expanduser('~/ProjectManager/GIT')
SVNFOLDER = os.path.expanduser('~/ProjectManager/SVN')

TYPES = ['LINK','GIT','SVN']

ACTIONS = {'LINK': ['open link'], 
           'GIT': ['code', 'git clone'],
           'SVN': ['code', 'svn checkout']}


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
    options = [f"{src['type']}: {src['name']}, {src['source']}" for src in resources]
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
    folder = make_folder(resource['type'], resource['name'])

    if action in ['open link',]:
        os.system(f"open {resource['source']}")

    elif action in ['code',]:
        if os.path.exists(folder) is True:
            os.system(f"code {folder}")
        else:
            print('Folder does not exist.')
    
    elif action in ['git clone',]:
        if os.path.exists(folder) is True:
            print(f'Folder {folder} already exist.')
        else:
            os.system(f"git clone {resource['source']} {folder}")
    
    elif action in ['svn checkout',]:
        if os.path.exists(folder) is True:
            print(f'Folder {folder} already exist.')
        else:
            os.system(f"svn checkout {resource['source']} {folder}")

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


if __name__ == '__main__':

    # Open the file and load its contents using the yaml library
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Parse arguments
    parser = argparse.ArgumentParser(description="Manage your projects.")
    parser.add_argument('--filter', type=comma_separated_list, help='A comma-separated list of words to filter')
    parser.add_argument('--showtags', action='store_true', help='Show tags that are used in data.')
    parser.add_argument('--cloneall', action='store_true', help='Clone all GIT repos.')
    parser.add_argument('--checkoutall', action='store_true', help='Checkout all SVN repos.')
    args = parser.parse_args()

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