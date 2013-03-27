import os
import re
import shutil
import sys
from cookbook_repo import *
from gitlib import *
from berkslib import *
from tag import Tag

def tag_compare(x, y):
    x_nums = x.split(".")
    y_nums = y.split(".")
    for (x,y) in zip(x_nums,y_nums):
        if x != y:
            return int(x) - int(y)
    return 0

def cleanup():
    if os.path.exists(".tina"):
        shutil.rmtree(".tina")

def recurse_discover_cookbooks(available_cookbooks, repos, root_repo):
    for depends in root_repo.metadata.depends:
        found = False
        for local_dir, cookbook in available_cookbooks.items():
            if cookbook.metadata.cookbook_name == depends:
                found = True
                if not cookbook.local_dir in repos:
                    cookbook.checkout()
                    repos[cookbook.metadata.cookbook_name] = cookbook
                    recurse_discover_cookbooks(available_cookbooks, repos, cookbook)
        if not found:
            print("%s depends on %s but it is not available" % (root_repo.metadata.cookbook_name, depends))
            exit()

def build_dependency_graph(repo_dict):
    parents = {}
    names = {}

    # Build a name dict for easily lookup of metadata dependencies.
    for _,repo in repo_dict.iteritems():
        parents[repo] = []
        names[repo.metadata.cookbook_name] = repo

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

def checkout_and_parse(path):
    cleanup()

    available_repos = repos_from_berks()
    available_cookbooks = {}

    root_url = get_local_repo_url()
    root_local_dir = get_name_from_url(root_url)

    available_repos[root_local_dir] = root_url
    repos = {}

    for local_dir, url in available_repos.items():
        cookbook = CookbookRepo(local_dir, url)
        available_cookbooks[cookbook.metadata.cookbook_name] = cookbook
        if local_dir == root_local_dir:
            root_cookbook = cookbook
            repos[root_cookbook.metadata.cookbook_name] = root_cookbook
            root_cookbook.checkout()

    recurse_discover_cookbooks(available_cookbooks, repos, root_cookbook) 

    build_dependency_graph(repos)

    print_summary(repos)
    generate_tinafile(repos)

def print_summary(repos):
    changed_repos = {}
    for _,repo in repos.items():
        format_str = "+%s (%s): %s" if repo.changed else "%s (%s): %s"
        print(format_str % (repo.metadata.cookbook_name, repo.new_tag, repo.url))


def generate_tinafile(repos):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# These are taggable cookbook repos. Repos prepended\n"
        "# with a + will have versions pinned, be tagged, and\n"
        "# will be pushed to their upstream remotes.\n")
   
    for _,repo in repos.items():
        format_str = "+%s: %s\n" if repo.changed else "%s: %s\n"
        tinafile.write(format_str % (repo.metadata.cookbook_name, repo.new_tag))

    tinafile.close()

def commit_and_push():
    repo_list, versions = parse_tinafile()

    for name in repo_list:
        cookbook_repo = CookbookRepo(name)
        cookbook_repo.changed = True
        cookbook_repo.new_tag = versions[name]
        cookbook_repo.resolve_deps(versions)
        #cookbook_repo.commit()

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
