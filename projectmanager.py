import yaml
import os
import inquirer

# Specify the path to the projects.yaml file
file_path = 'projects.yaml'

GITFOLDER = os.path.expanduser('~/ProjectManager/GIT')
SVNFOLDER = os.path.expanduser('~/ProjectManager/SVN')

TYPES = ['LINK','GIT','SVN']

ACTIONS = {'LINK': ['open link'], 
           'GIT': ['git clone', 'code'],
           'SVN': []}


# lnk = projects_data['24 Strike Back Against Self-Suspension']['resources'][1]['link']

# print(lnk)
# # os.system(f"open -a iterm ~/Testfolder/.")
# os.system(f"git clone {lnk} ~/Testfolder/.")

# # os.system(f"open {lnk}")
# # os.system(f"code .")

# # pth = "~/Documents/GIT/SAG/."

# # os.system(f"open  ")


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

    if action in ['open link',]:
        os.system(f"open {resource['source']}")
    elif action in ['code',]:
        # check if folder exists:
        if resource['type'] == 'GIT':
            folder = os.path.join(GITFOLDER,resource['name'])
        elif resource['type'] == 'SVN':
            folder = os.path.join(SVNFOLDER,resource['name'])
        if os.path.exists(folder) is True:
            os.system(f"code {folder}")
        else:
            print('Folder does not exist. Choose another action.')
            return 2
    elif action in ['git clone',]:
        # check if folder exists:
        folder = os.path.join(GITFOLDER,resource['name'])
        breakpoint()
        if os.path.exists(folder) is True:
            print(f'Folder {folder} already exist. Choose another action.')
            return 2
        else:
            os.system(f"git clone {resource['source']} {folder}")
            return 4
    else:
        print('Action not found.')
        exit()



if __name__ == '__main__':

    # Open the file and load its contents using the yaml library
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

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