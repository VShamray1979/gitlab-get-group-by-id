"""
This script allows you to clone all projects for a given group and its subgroups from a GitLab instance using the GitLab API.

Before using this script, you need to install the 'python-gitlab' package by running: pip install python-gitlab

You also need to provide the following information:
- GitLab URL
- GitLab API token with 'api' scope
- Path where to clone the group projects
- Id of the root group to clone

Then, run the script and it will clone all projects for the specified group and its subgroups into the provided path.
For run use:
python3 get-group-by-id.py group_id -p /path/to/clone/projects
Example:
python3 get-group-by-id.py 6184 --path /home/user/gitlab-projects
"""
import gitlab
import os
import sys
import argparse

# GitLab API token
TOKEN='YOUR_TOKEN'
# GitLab URL
URL='https://gitlab.com'

def clone_projects(parent_path, group):
  # Define the path where to clone the repository
  group_path = os.path.join(parent_path, group.path)

  # Create the directory if it doesn't exist
  if not os.path.exists(group_path):
    os.makedirs(group_path)

  # Clone the projects in the group
  for project in group.projects.list(get_all=True):
    project_path = os.path.join(group_path, project.path)
    git_path = os.path.join(project_path, ".git")
    if not os.path.exists(git_path):
      print(f"Cloning project {project_path}")
      os.system(f"git clone {project.ssh_url_to_repo} {project_path}")
    else:
      print(f"Project '{project.name}' already exist {project_path}")

  # Recursively clone projects in subgroups
  for subgroup in group.subgroups.list(get_all=True):
    clone_group_projects(group_path, subgroup.id)

def clone_group_projects(parent_path, group_id):
  try:
    group = gl.groups.get(group_id)
  except (gitlab.exceptions.GitlabHttpError, gitlab.exceptions.GitlabGetError):
    print("Failed to find group in GitLab. Please check Id.")
    sys.exit(1)
  clone_projects(parent_path, group)

# MAIN
# Check arguments
parser = argparse.ArgumentParser(description='Clone all projects in a GitLab group.')
parser.add_argument('group_id', type=str, help='Id of the GitLab group')
parser.add_argument('-p', '--path', type=str, default=os.getcwd(), help='Path where to clone the group projects')

args = parser.parse_args()

group_id = args.group_id
path = args.path

# Connect to GitLab and check that authentification is success
try:
    gl = gitlab.Gitlab(URL, private_token=TOKEN)
    gl.auth()
except gitlab.exceptions.GitlabAuthenticationError:
    print("Failed to authenticate with GitLab. Please check your API token.")
    sys.exit(1)

# Run the function to clone the group projects
clone_group_projects(path, group_id)
