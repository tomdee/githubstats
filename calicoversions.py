import re
from bs4 import BeautifulSoup
import pprint
pp = pprint.PrettyPrinter(indent=4)

# I want to find
# a) the versions for a particular release
# b) the PRs that went in since that release
# For now, just treat a) as the top version on http://docs.projectcalico.org/v2.0/releases/

components  = {}
soup = BeautifulSoup(open("index.html"), "html.parser")

top_table = soup.find("table")
version = top_table.find_previous("h2").string.split(' ')[0] # Everything before the first space
rows = top_table.find("tbody")("tr")
for row in rows:
    cells = row("td")
    components[cells[0].string] = cells[1].string
    # print "%s %s" % (, )

pp.pprint(components)
# for table in soup("table"):
#     print table.find_previous("h2").string


from github import Github
from prettytable import PrettyTable


# First create a Github instance:
g = Github(login_or_token=os.environ["GITHUB_API_TOKEN"])

def get_PRs(repo, last_version):
    prs = []
    for commit in repo.compare(last_version, "master").commits:
        title = commit.commit.message.splitlines()[0]
        m = re.search("Merge pull request #(\d+)", title)
        if m:
            prs.append(m.group(1))
        # else:
        #     print "didn't find a commit in %s" % title
    return prs


repo = g.get_repo("projectcalico/calicoctl")
for pr_number in get_PRs(repo, "v1.0.0"):
    pr = repo.get_pull(int(pr_number))
    print "PR #%s (%s) - %s" % (pr.number, pr.user.login, pr.title)
