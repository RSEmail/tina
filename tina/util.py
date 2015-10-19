import git
import json
import os
import re
import shutil
import subprocess

import config

def rmdir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)

def cleanup():
    rmdir('.tina')

def run_berks(berksfile=None):
    berks_groups = config.TinaConfig.berks_groups
    args = ['berks', 'vendor', '.tina', '--format=json']
    if berksfile:
        args.append('--berksfile={0}'.format(berksfile))
    if berks_groups:
        args.append('--except={0}'.format(' '.join(berks_groups)))

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    berks_output, errors = proc.communicate()
    return json.loads(berks_output)

def get_cookbook_information(berks_output):
    cookbooks = {}
    cookbooks['local'] = {}
    cookbooks['community'] = {}
    location_re = re.compile('^([\w\.-]+@[\w\.-]+:[\w\.-]+\/[\w\.-]+) .*')

    for cookbook in berks_output['cookbooks']:
        if 'location' in cookbook:
            match = location_re.match(cookbook['location'])
            if match:
                name = cookbook['name'].split()[0]
                location = match.group(1)
                cookbooks['local'][name] = location
        else:
            name = cookbook['name']
            version = cookbook['version']
            cookbooks['community'][name] = version

    return cookbooks

def get_repo(repo_name):
    repo_dir = os.path.join('.tina', repo_name)
    return git.Repo(repo_dir)

def search_for_repo(repo_name):
    user = config.TinaConfig.git_user
    url = config.TinaConfig.git_url
    orgs = config.TinaConfig.git_orgs

    repos = ['{0}@{1}:{2}'.format(user, url, org) for org in orgs]

    success = False
    target_dir = os.path.join('.tina', repo_name)
    for repo in repos:
        try:
            repo_url = '{0}/{1}.git'.format(repo, repo_name)
            return git.Repo.clone_from(repo_url, target_dir)
        except Exception:
            continue

    raise ValueError('Could not find repo: {0}'.format(repo_name))

def checkout_repo(repo_name, repo_url):
    print 'Cloning {0}...'.format(repo_name)
    local_path = os.path.join('.tina', repo_name)
    rmdir(local_path)

    return git.Repo.clone_from(repo_url, local_path)
