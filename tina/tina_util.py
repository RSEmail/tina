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

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)

def build_repo_dict(git_urls):
    repos = {}
    i = 0
    for repo_url in git_urls:
        sys.stdout.write("\rCloning repositories [%d/%d]" % (i, len(git_urls)))
        name = get_name_from_url(repo_url)
        repo = CookbookRepo(name, repo_url)
        repos[repo_url] = repo
        i = i + 1
    print "\rCloning repositories [%d/%d]" % (i, len(git_urls))
    return repos

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

    git_repos = get_git_urls_from_file(os.path.join(path, "Berksfile"))
    git_repos.append(get_local_repo_url())
    repo_dict = build_repo_dict(git_repos)
    build_dependency_graph(repo_dict)

    versions = { }
    cookbook_names = [ ]

    for _,repo in repo_dict.items():
        versions[repo.metadata.cookbook_name] = repo.new_tag
        cookbook_names.extend(repo.metadata.depends)

    cookbook_names = list(set(cookbook_names))
    community_cookbooks = CommunityCookbooks(cookbook_names)

    print_summary(repo_dict, community_cookbooks.versions)
    generate_tinafile(repo_dict, community_cookbooks.versions)

def print_summary(repos, cookbooks):
    print "REPOSITORY SUMMARY:"
    for _,repo in repos.items():
        if repo.changed:
            print "%s: %s => %s" % (repo.name, repo.old_tag, repo.new_tag)
        else:
            print "%s: unchanged" % repo.name

    print
    print "COMMUNITY COOKBOOK SUMMARY:"
    for name,version in cookbooks.items():
        print "%s will be pinned at %s" % (name, version)

def generate_tinafile(repos, cookbooks):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# These are taggable cookbook repos. Repos prepended\n"
        "# with a + will have versions pinned, be tagged, and\n"
        "# will be pushed to their upstream remotes.\n")

    for _,repo in repos.items():
        format_str = "+%s: %s\n" if repo.changed else "%s: %s\n"
        tinafile.write(format_str % (repo.metadata.cookbook_name, repo.new_tag))

    tinafile.write("# Pinned community cookbooks:\n")
    for name,version in cookbooks.items():
        tinafile.write("%s: %s\n" % (name, version))

    tinafile.close()

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
