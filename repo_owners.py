from github import Github
import os

# Check for missing or misconfigured desired teams
def compare(desired, actual):
    actual.sort()
    desired.sort()
    if actual != desired:
        return "Desired: %s Actual: %s" % (desired, actual)


def get_logins():
    users = []
    for user in g.get_organization("projectcalico").get_members():
        users.append(user.login)

# # First create a Github instance:
g = Github(login_or_token=os.environ["GITHUB_API_TOKEN"])
o = g.get_organization("projectcalico")

# o.create_team("libnetwork-plugin-maintainers", [o.get_repo("libnetwork-plugin")])
desired_teams = {
    "libnetwork-plugin-maintainers": {"repos": ["libnetwork-plugin"], "users": ["tomdee", "robbrockbank"]},
    "libcalico-go-maintainers": {"repos": ["libcalico-go"], "users": ["fasaxc", "robbrockbank", "caseydavenport"]},
    "go-build-maintainers": {"repos": ["go-build"], "users": ["fasaxc", "tomdee"]},
    "felix-maintainers": {"repos": ["felix"], "users": ["fasaxc", "neiljerram"]},
    "cni-plugin-maintainers": {"repos": ["cni-plugin"], "users": ["tomdee", "caseydavenport"]},
    "canal-maintainers": {"repos": ["canal"], "users": ["tomdee", "caseydavenport"]},
    "calicoctl-maintainers": {"repos": ["calicoctl"], "users": ["tomdee", "robbrockbank", "caseydavenport"]},
    "calico-maintainers": {"repos": ["calico"], "users": ["djosborne", "robbrockbank"]},
    "calico-bgp-daemon-maintainers": {"repos": ["calico-bgp-daemon"], "users": ["gunjan5", "robbrockbank"]},
    "bird-maintainers": {"repos": ["bird"], "users": ["neiljerram", "robbrockbank"]},
    "calico-dcos-maintainers": {"repos": ["calico-dcos"], "users": ["djosborne", "robbrockbank"]},
    "k8s-policy-maintainers": {"repos": ["k8s-policy"], "users": ["caseydavenport"]},
    "calico-k8s-cluster-maintainers": {"repos": ["calico-k8s-cluster"], "users": ["caseydavenport"]},
"Build Machines": {"repos": ["felix"], "users": ["marvin-tigera"]},
    "Calico": {
        "repos": ["calico-dnsmasq", "calico-nova", "calico-neutron", "felix", "calico-chef", "fuel-library",
                  "calicoctl", "python-etcd", "bird", "calico-kubernetes-coreos-demo",
                  "calico-kubernetes-ubuntu-demo", "netmodules-plugin", "libcalico", "cni-plugin",
                  "k8s-exec-plugin", "libnetwork-plugin", "posix_spawn", "confd", "dind", "datrie", "ijson",
                  "etcd-ca", "test-ca", "mesos-nettest-framework", "docker-compose-kubernetes", "k8s-policy",
                  "cfssl", "calico-dcos", "charm-neutron-api", "charm-openstack-dashboard", "calico-k8s-cluster",
                  "star", "canal", "charm-neutron-calico", "bundle-openstack-calico", "prometheus-client-python",
                  "charm-bird", "charm-etcd", "layer-etcd-proxy", "libcalico-go", "calico", "calico-bgp-daemon",
                  "go-yaml-wrapper", "go-yaml", "go-json", "netlink", "go-build"]
        , "users": ["TomBlossom", "ahrkrak", "caseydavenport", "djosborne", "doublek", "fasaxc", "frnkdny",
                    "gunjan5", "heschlie", "kprabhak", "liljenstolpe", "lwr20", "lxpollitt", "matthewdupre",
                    "mikestowe", "neiljerram", "robbrockbank", "tmjd", "tomdee"]},

}

# teams = [x.name for x in g.get_organization("projectcalico").get_repos()]
# print teams
#
# import sys
#
# sys.exit(1)

# Do a check of the repos and make sure they only have the right team
repo_teams = {}
for team, v in desired_teams.iteritems():
    for repo in v["repos"]:
        if not repo_teams.get(repo):
            repo_teams[repo] = []
        repo_teams[repo].append(team)

for repo in g.get_organization("projectcalico").get_repos():
    teams = [x.name for x in repo.get_teams()]
    assert repo_teams.get(repo.name)
    # We have a specific list of teams for this repo
    membership_diffs = compare(repo_teams.get(repo.name), teams)

    if membership_diffs:
        print "Repo %s has incorrect team membership. %s" % (repo.name.ljust(30), membership_diffs)

existing_teams = {}
for team in g.get_organization("projectcalico").get_teams():
    existing_teams[team.name] = team

# Create all the teams - making sure that at least the required state exists (doens't check for additional state)
for k, v in desired_teams.iteritems():
    team = existing_teams.get(k)
    if not team:
        team = o.create_team(k, [o.get_repo(x) for x in v["repos"]], "admin")
        print "Creating team: %s" % k
    for repo in v["repos"]:
        if not team.has_in_repos(o.get_repo(repo)):
            print "Adding %s to %s" % (repo, k)
            team.add_to_repos(o.get_repo(repo))
    for user in v["users"]:
        if not team.has_in_members(g.get_user(user)):
            team.add_to_members(g.get_user(user))
            print "Adding %s to %s" % (user, k)

# Now do an exact compare on the teams to make sure there isn't extra data
# Check for unwanted existing teams
for _, existing_team in existing_teams.iteritems():
    if not desired_teams.get(existing_team.name):
        print "Existing team (%s) is not desired" % existing_team.name

for k, v in desired_teams.iteritems():
    existing_team = existing_teams.get(k)
    if existing_team:
        user_diff = compare(v["users"], [x.login for x in existing_team.get_members()])
        repos_diff = compare(v["repos"], [x.name for x in existing_team.get_repos()])

        if user_diff or repos_diff:
            print "Existing team (%s) is misconfigured.\n  User Diff: %s\n  Repos Diff: %s" % (k, user_diff, repos_diff)
        else:
            print "Existing team %s is all good" % k
    else:
        print "Desired team (%s) doesn't exist" % k

#List of users:
"""
ahrkrak
caseydavenport
djosborne
doublek
fasaxc
frnkdny
gunjan5
heschlie
liljenstolpe
lwr20
lxpollitt
matthewdupre
neiljerram
robbrockbank
tmjd
tomdee
"""
