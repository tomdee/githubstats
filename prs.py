from github import Github
from prettytable import PrettyTable
from slackclient import SlackClient
import os

slack_token = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(slack_token)


# # First create a Github instance:
g = Github(login_or_token=os.environ["GITHUB_API_TOKEN"])
all_open_prs = g.search_issues('is:open is:pr user:projectcalico')
all_open_issues = g.search_issues('is:open is:issue user:projectcalico')
all_open_issues_milestone = g.search_issues('is:open user:projectcalico milestone:"Calico v2.1.0"')

message = ""

def check_labels(labels):
    label = ""
    if "kind/support" in [x.name for x in labels]:
        label += "Support"
    elif "kind/bug" in [x.name for x in labels]:
        label += "Bug"
    elif "kind/enhancement" in [x.name for x in labels]:
        label += "Enhancement"

    if label == "":
        label = "No type"
    return label


def get_table(title, issues, extract):
    x = PrettyTable()
    x.title = title
    counts = dict()

    for issue in issues:
        extracted = extract(issue)
        counts[extracted] = counts.get(extracted, 0) + 1

    count_header = "Things (total=%s)" % sum(counts.values())
    x.field_names = ["Name", count_header]
    x.sortby = count_header
    x.reversesort = True
    for k, v in counts.iteritems():
        x.add_row([k, v])
    return str(x)

def get_issues_by_repo_and_type(issues):
    x = PrettyTable()
    x.title = "Open issues by repo and type"
    counts = dict()

    for issue in issues:
        label = check_labels(issue.labels)
        repo = issue.url.split('/')[-3]
        if not counts.get(repo):
            counts[repo] = dict()

        counts[repo]['Total'] = counts[repo].get('Total', 0) + 1
        counts[repo][label] = counts[repo].get(label, 0) + 1

    x.field_names = ["Name", "Total", "Bug", "Enhancement", "Support", "No type"]
    x.sortby = "Total"
    x.reversesort = True
    for k in counts.iterkeys():
        x.add_row([k, counts[k]["Total"], counts[k].get("Bug", 0), counts[k].get("Enhancement", 0), counts[k].get("Support", 0), counts[k].get("No type", 0)])
    return str(x) + "\n"

message += "```\n"
message +=  "*** PR summary ***\n"
message += get_table("PRs by raiser", all_open_prs, lambda x: x.user.login)
message += get_table("PRs by assignee", all_open_prs, lambda x: x.assignee.login if x.assignee else "Unassigned")
message += get_table("PRs by repo", all_open_prs, lambda x: x.url.split('/')[-3])
message += "```\n"
message += "```\n"
message += "*** Issues summary ***\n"
message += get_table("Issues by type ", all_open_issues, lambda x: check_labels(x.labels))
message += get_table("Issues by repo", all_open_issues, lambda x: x.url.split('/')[-3])
message += get_issues_by_repo_and_type(all_open_issues) + "\n"
message += "```\n"
message += "```\n"
message += "\n*** Release issues summary ***\n"
message += get_table("v2.1 milestone issues by assignee", all_open_issues_milestone, lambda x: x.assignee.login if x.assignee else "Unassigned")
message += get_table("v2.1 milestone issues by repo", all_open_issues_milestone, lambda x: x.url.split('/')[-3])
message += "```\n"
print message

# TODO - Unreleased PRs merged by project since last release
sc.api_call(
  "chat.postMessage",
  channel=os.environ.get("SLACK_CHANNEL", "@tom"),
  text=message
)
