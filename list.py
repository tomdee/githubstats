from github import Github
import os

# # First create a Github instance:
g = Github(login_or_token=os.environ["GITHUB_API_TOKEN"])

for repo in g.get_organization("projectcalico").get_repos():
    if  repo.fork:
        print repo.name

