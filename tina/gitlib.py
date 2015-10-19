import git
import os

import config

def find_repo(repo_name):
    user = config.TinaConfig.git_user
    url = config.TinaConfig.git_url
    orgs = config.TinaConfig.git_orgs

    repos = ['{0}@{1}:{2}'.format(user, url, org) for org in orgs]

    success = False
    target_dir = os.path.join('.tina', repo_name)
    for repo in repos:
        try:
            repo_url = '{0}/{1}.git'.format(repo, repo_name)
            git.Repo.clone_from(repo_url, target_dir)
            success = True
        except Exception:
            continue

    if not success:
        raise ValueError('Could not find repo: {0}'.format(repo_name))

def checkout_repo(repo_name, repo_url):
    print 'Cloning {0}...'.format(repo_name)
    local_path = os.path.join('.tina', repo_name)
    return git.Repo.clone_from(repo_url, local_path)
