import os
import re
import shutil
import sys
from cookbook_repo import *
from gitlib import *
from parse_berk import *
from community_cookbooks import *
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

def recurse_discover_cookbooks(available_cookbooks, taggable_cookbooks, dependent_cookbooks, root_repo):
    for depends in root_repo.metadata.depends:
        dependent_cookbooks[depends] = True
        found = False
        for cookbook in available_cookbooks:
            if cookbook["name"] == depends:
                found = True
                if cookbook["taggable"]:
                    if not cookbook["name"] in taggable_cookbooks.keys():
                        taggable_cookbooks[cookbook["name"]] = CookbookRepo(get_name_from_url(cookbook["rw_url"]), cookbook["rw_url"])
                        recurse_discover_cookbooks(available_cookbooks, taggable_cookbooks, dependent_cookbooks, taggable_cookbooks[cookbook["name"]])
        if not found:
            print("%s depends on %s but it is not available" % (root_repo.metadata.cookbook_name, depends))
            exit()

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)

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

    available_cookbooks = cookbooks_from_berks()
    local_url = get_local_repo_url()
    local_name = get_name_from_url(local_url)
    root_repo = CookbookRepo(local_name, local_url)

    taggable_repos = {}
    dependent_cookbooks = {}
    taggable_repos[root_repo.metadata.cookbook_name] = root_repo
    recurse_discover_cookbooks(available_cookbooks, taggable_repos, dependent_cookbooks, root_repo) 

    build_dependency_graph(taggable_repos)

    print_summary(taggable_repos, available_cookbooks, dependent_cookbooks)
    generate_tinafile(taggable_repos, available_cookbooks, dependent_cookbooks)

def print_summary(taggable_repos, available_cookbooks, dependent_cookbooks):
    changed_repos = {}
    for _,repo in taggable_repos.items():
        format_str = "+%s (%s): %s" if repo.changed else "%s (%s): %s"
        print(format_str % (repo.metadata.cookbook_name, repo.new_tag, repo.url))
        changed_repos[repo.metadata.cookbook_name] = repo

    for cookbook_name, _ in dependent_cookbooks.items():
        if not cookbook_name in changed_repos:
            for available in available_cookbooks:
                if available["name"] == cookbook_name:
                    print("%s (%s): %s" % (available["name"], available["version"], available["location"]))


def generate_tinafile(taggable_repos, available_cookbooks, dependent_cookbooks):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# These are taggable cookbook repos. Repos prepended\n"
        "# with a + will have versions pinned, be tagged, and\n"
        "# will be pushed to their upstream remotes.\n")
   
    changed_repos = {}
    for _,repo in taggable_repos.items():
        format_str = "+%s: %s\n" if repo.changed else "%s: %s\n"
        tinafile.write(format_str % (repo.metadata.cookbook_name, repo.new_tag))
        changed_repos[repo.metadata.cookbook_name] = repo

    tinafile.write("# Dependency cookbooks:\n")
    for cookbook_name, _ in dependent_cookbooks.items():
        if not cookbook_name in changed_repos:
            for available in available_cookbooks:
                if available["name"] == cookbook_name:
                    tinafile.write("%s: %s\n" % (available["name"], available["version"]))

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
