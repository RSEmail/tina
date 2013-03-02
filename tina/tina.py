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

def main():
    cleanup()
    git_repos = get_git_urls_from_file('./Berksfile')
    git_repos.append(get_local_repo_url())
    versions = {}
    cookbook_names = []
    repos = []
    any_changed = False

    for repo_url in git_repos:
        repo = CookbookRepo(repo_url)
        any_changed = repo.changed or any_changed
        versions[repo.metadata.cookbook_name] = repo.new_tag
        cookbook_names.extend(repo.metadata.depends)
        repos.append(repo)

    # This is a hack
    for repo in repos:
        repo.changed = any_changed
        repo.version_bump()
        versions[repo.metadata.cookbook_name] = repo.new_tag

    cookbook_names = list(set(cookbook_names)) 
    community_cookbooks = CommunityCookbooks(cookbook_names)
    combined_versions = dict(versions.items() + community_cookbooks.versions.items())
    print("All cookbooks found: %s" % combined_versions)

    for repo in repos:
        repo.resolve_deps(combined_versions)
        repo.commit()

if __name__ == "__main__":
    main()
