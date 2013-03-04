import shutil
import os
from CookbookRepo import *
from CommunityCookbooks import *
from GitLib import *
from ParseBerk import *

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
    for repo_url in git_urls:
        repos[repo_url] = CookbookRepo(repo_url)
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

def main():
    print "Cloning repositories..."
    cleanup()
    git_repos = get_git_urls_from_file('./Berksfile')
    git_repos.append(get_local_repo_url())
    repo_dict = build_repo_dict(git_repos)
    build_dependency_graph(repo_dict)

    versions = {}
    cookbook_names = []
    print "Repository summary:"
    for _,repo in repo_dict.iteritems():
        if repo.changed:
            print "%s: %s => %s" % (repo.name, repo.old_tag, repo.new_tag)
        else:
            print "%s: unchanged" % repo.name

        versions[repo.metadata.cookbook_name] = repo.new_tag
        cookbook_names.extend(repo.metadata.depends)

    cookbook_names = list(set(cookbook_names)) 
    community_cookbooks = CommunityCookbooks(cookbook_names)
    combined_versions = dict(versions.items() + community_cookbooks.versions.items())

    for _,repo in repo_dict.iteritems():
        repo.resolve_deps(combined_versions)
        repo.commit()

if __name__ == "__main__":
    main()
