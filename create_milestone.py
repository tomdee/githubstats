from github import Github
import os

# # First create a Github instance:
from github import GithubException

g = Github(login_or_token=os.environ["GITHUB_API_TOKEN"])

milestone_repos = [
    "felix",
    "calicoctl",
    "bird",
    "cni-plugin",
    "libnetwork-plugin",
    "libcalico-go",
    "calico",
    "calico-bgp-daemon"]

print "Creating new milestone"
for repo in milestone_repos:
    try:
        g.get_organization("projectcalico").get_repo(repo).create_milestone("Calico v2.1.X")
        print "Created milestone for %s" % repo
    except GithubException as e:
        print "Failed to create milestone for %s" % repo

print "Current milestones:"
for repo in g.get_organization("projectcalico").get_repos():
    for milestone in repo.get_milestones():
        print "%s: O:%s C:%s %s Due: %s %s" % (repo.name, milestone.open_issues, milestone.closed_issues,milestone.title,  milestone.due_on,  milestone.url.replace("https://api.github.com/repos/", "https://github.com/").replace("milestones", "milestone"))



