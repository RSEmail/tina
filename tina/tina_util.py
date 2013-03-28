import os
import shutil
import sys
from cookbook_repo import *
from gitlib import *
from parse_berk import *
from community_cookbooks import *

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

def build_repo_dict(git_urls):
    repos = {}
    i = 0
    for repo_url in git_urls:
        sys.stdout.write("\rCloning repositories [%d/%d]" % (i, len(git_urls)))
        repo = CookbookRepo(repo_url)
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

    combined_versions = dict(versions.items() + community_cookbooks.versions.items())
    for _,repo in repo_dict.iteritems():
        repo.resolve_deps(combined_versions)

def print_summary(repos, cookbooks):
    print "REPOSITORY SUMMARY:"
    for _,repo in repos.items():
        if repo.changed:
            print "%s: %s => %s" % (repo.name, repo.old_tag, repo.new_tag)
        else:
            print "%s: unchanged" % repo.name

    print
    print "COOKBOOK SUMMARY:"
    for name,version in cookbooks.items():
        print "%s will be pinned at %s" % (name, version)

def generate_tinafile(repos, cookbooks):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# Taggable git repos:\n")
    for _,repo in repos.items():
        if repo.changed:
            tinafile.write("%s: %s\n" % (repo.name, repo.new_tag))

    tinafile.write("# Pinned community cookbooks:\n")
    for name,version in cookbooks.items():
        tinafile.write("+%s: %s\n" % (name, version))

    tinafile.close()
