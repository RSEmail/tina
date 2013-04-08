import fileinput
import os
import re
import shutil
import sys
from collections import defaultdict
from cookbook_repo import *
from gitlib import *
from berkslib import *
from tag import Tag
from operator import attrgetter

def cleanup():
    if os.path.exists(".tina"):
        shutil.rmtree(".tina")

def discover_cookbooks(available_cookbooks, repos, root_repo):
    for depends in root_repo.metadata.depends:
        found = False
        for local_dir, cookbook in available_cookbooks.items():
            if cookbook.name == depends:
                found = True
                if not cookbook.local_dir in repos:
                    cookbook.checkout()
                    repos[cookbook.name] = cookbook
                    discover_cookbooks(available_cookbooks, repos,
                        cookbook)
        if not found:
            print "%s depends on %s but it is not available" % \
                (root_repo.name, depends)
            exit()

def build_repo_dict(available_repos, root_dir):
    cookbooks = {}
    repos = {}
    root_cookbook = None

    for local_dir, url in available_repos.items():
        cookbook = CookbookRepo(local_dir, available_repos[local_dir])
        cookbooks[cookbook.name] = cookbook
        if local_dir == root_dir:
            root_cookbook = cookbook
            repos[root_cookbook.name] = root_cookbook
            root_cookbook.checkout()

    print "Discovering dependent cookbooks..."
    discover_cookbooks(cookbooks, repos, root_cookbook)
    return repos

def check_version_conflicts(repos):
    print "Checking for version conflicts..."
    metadatas = [repo.metadata for repo in repos.values()]
    requirements = defaultdict(list)
    for metadata in metadatas:
        for name, requirement in metadata.requirements.items():
            requirements[name].append(requirement)

    incompatibility = False
    for name in requirements.keys():
        for i, req1 in enumerate(requirements[name]):
            for req2 in requirements[name][i+1:]:
                if not req1.compatible_with(req2):
                    print("Error: %s requires %s %s %s, but %s requires %s %s %s" %
                        (req1.dependence, req1.name, req1.operator, req1.version,
                        req2.dependence, req2.name, req2.operator, req2.version))
                    incompatibility = True
    if incompatibility:
        print "Please resolve the above version conflicts and re-run TINA"

    return incompatibility


def build_dependency_graph(repo_dict):
    print "Resolving dependencies..."
    parents = {}
    names = {}

    # Build a name dict for easily lookup of metadata dependencies.
    for _,repo in repo_dict.iteritems():
        parents[repo] = []
        names[repo.name] = repo

    for _,repo in repo_dict.iteritems():
        child_repos = repo.metadata.depends
        for name in child_repos:
            # Assume that if this cookbook name isn't in the dict, then
            # it's a community cookbook.
            if name in names:
                child = names[name]
                if not repo in parents[child]:
                    parents[child].append(repo)

    for _,repo in repo_dict.iteritems():
        if repo.changed:
            for parent in parents[repo]:
                resolve_dependencies(parents, parent)

def resolve_dependencies(graph, repo):
    if repo.changed:
        return
    repo.changed = True
    repo.version_bump()
    for parent in graph[repo]:
        resolve_dependencies(graph, parent)

def checkout_and_parse(path, interactive):
    cleanup()

    root_url = get_local_repo_url()
    root_local_dir = get_name_from_url(root_url)

    available_repos = repos_from_berks()
    available_repos[root_local_dir] = root_url

    repos = build_repo_dict(available_repos, root_local_dir)
    if check_version_conflicts(repos): sys.exit(1)
    build_dependency_graph(repos)

    repo_list = repos.values()
    sort_repos(repo_list)
    print_summary(repo_list)
    if interactive: gather_user_input(repo_list)
    generate_tinafile(repo_list)

def sort_repos(repos):
    repos.sort(key=attrgetter("url"), reverse=True)

def print_summary(repos):
    print "REPOSITORY SUMMARY:"
    for i, repo in enumerate(repos):
        if repo.url:
            if repo.changed:
                print "%d. %s: %s => %s" % ((i+1, repo.name, repo.old_tag,
                    repo.new_tag))
            else:
                print "%d. %s: unchanged" % (i+1, repo.name)
        else:
            print "%d. %s will be pinned at %s" % (i+1, repo.name,
                repo.new_tag)


def generate_tinafile(repos):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# These are taggable cookbook repos. Repos prepended\n"
        "# with a + will have versions pinned, be tagged, and\n"
        "# will be pushed to their upstream remotes.\n")
   
    for repo in repos:
        format_str = "+%s: %s\n" if repo.changed else "%s: %s\n"
        tinafile.write(format_str % (repo.name, repo.new_tag))

    tinafile.close()

def gather_user_input(repos):
    prompt = "Enter a repository index to modify, 'p' to print summary, " \
        "'q' to quit: "
    while True:
        line = raw_input(prompt)
        if line == "q": break
        if line == "p":
            print_summary(repos)
            continue

        try:
            n = int(line)
            if n < 1 or n >= len(repos):
                print "Invalid repo index: %d" % n
                continue

            repo = repos[n-1]
            if repo.url:
                if repo.changed:
                    modify_changed_repo(repo)
                else:
                    modify_unchanged_repo(repo)
            else:
                modify_community_cookbook(repo)
        except ValueError:
            print "Unrecognized option: %s" % line

def modify_changed_repo(repo):
    print "%s will be tagged as %s" % (repo.name, repo.new_tag)
    print "1. Mark unchanged"
    print "2. Bump build number"
    print "3. Bump minor version"
    print "4. Bump major version"
    print "5. Do nothing"

    user_input = raw_input("Choose one of the above options: ")
    try:
        n = int(user_input)
        if n == 1:
            repo.changed = False
            repo.new_tag = repo.old_tag
        elif n > 1 and n < 5:
            repo.version_bump(n-1)
        elif n == 5:
            return
        else:
            print "Unrecognized option: %s" % user_input
    except ValueError:
        print "Unrecognized option: %s" % user_input

    if repo.changed:
        print "%s will now be tagged as %s" % (repo.name, repo.new_tag)
    else:
        print "%s is now unchanged" % repo.name

def modify_unchanged_repo(repo):
    print "%s is unchanged and does not need to be tagged" % repo.name
    print "1. Mark changed"
    print "2. Do nothing"

    user_input = raw_input("Choose one of the above options: ")
    try:
        n = int(user_input)
        if n == 1:
            repo.changed = True
        elif n == 2:
            return
        else:
            print "Unrecognized option: %s" % user_input
    except ValueError:
        print "Unrecognized option: %s" % user_input

    if repo.changed:
        print "%s will now be tagged as %s" % (repo.name, repo.new_tag)

def modify_community_cookbook(repo):
    print "%s is a community cookbook, and will be pinned at %s" % \
        (repo.name, repo.new_tag)
    print "1. Modify pinned version"
    print "2. Do nothing"

    user_input = raw_input("Choose one of the above options: ")
    try:
        n = int(user_input)
        if n == 1:
            repo.new_tag = Tag(raw_input("Enter new version: "))
        elif n == 2:
            return
        else:
            print "Unrecognized option: %s" % user_input
    except ValueError:
        print "Unrecognized option: %s" % user_input

def commit_and_push():
    repo_list, versions = parse_tinafile()

    for name in repo_list:
        cookbook_repo = CookbookRepo(name)
        cookbook_repo.changed = True
        cookbook_repo.new_tag = versions[name]
        cookbook_repo.resolve_deps(versions)
        cookbook_repo.commit()

def parse_tinafile():
    tinafile = open(".tina/Tinafile", "r")
    lines = tinafile.readlines()

    repo_list = [ ]
    versions = { }
    cookbook_regex = re.compile("^(\+?)([\w\-\.]+)\s*:\s*([\w\-\.]+)\s*$")
    for line in lines:
        if line[0] == "#":
            continue

        line = line.rstrip()
        match = cookbook_regex.match(line)
        if not match:
            raise Exception("Invalid line in Tinafile: '%s'" % line)

        versions[match.group(2)] = Tag(match.group(3))
        if match.group(1) == "+":
            repo_list.append(match.group(2))

    tinafile.close()
    return repo_list, versions
