import git
import os
import re
from cookbook_metadata import *
from tag import Tag

def checkout_repo(repo_name, repo_url):
    local_path = ".tina/" + repo_name
    print("Cloning %s" % repo_url)
    return git.Repo.clone_from(repo_url, local_path)

def get_tag_of_repo(repo):
    tags = repo.tags
    if len(tags) is 0:
        return None

    tag_list = []
    for tag in tags:
        try:
            tag_list.append(Tag(str(tag)))
        except Exception:
            pass

    tag_list.sort()
    return tag_list[-1]

def get_local_repo_url():
    repo = git.Repo(".")
    origin = repo.remotes.origin
    return origin.url

def create_tag(repo, tag):
    repo.index.add(['metadata.rb'])
    repo.index.commit('Tagging for %s.' % tag)
    repo.create_tag(tag)

def commit_and_push(repo, name, tag):
    try:
        print "Pushing %s..." % name
        create_tag(repo, str(tag))
        repo.remotes.origin.push('--tags')
    except git.GitCommandError as e:
        print ("Problem committing to '%s', error was '%s'" % (name, e.command))
        raise
