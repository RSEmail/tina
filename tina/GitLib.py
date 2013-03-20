import git
import os
import re
from tina import *
from CookbookMetadata import *

def checkout_repo(repo_url):
    regex = re.compile(".*/(.+?)\.git.*")
    match = regex.match(repo_url)
    repo_name = ""
    if match:
        local_path = ".tina/" + match.group(1)
        return git.Repo.clone_from(repo_url, local_path)
    else:
        raise SyntaxError("URL is malformed: '%s'" % url)

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)

def get_tag_of_repo(repo):
    tags = repo.tags
    if len(tags) is 0:
        return None

    tag_regex = re.compile("v(\d+\.\d+\.\d+)")
    tag_list = []
    for tag in tags:
        tag_match = tag_regex.match(str(tag))
        if tag_match:
            tag_list.append(tag_match.group(1))
    tag_list.sort(cmp=tag_compare)

    return tag_list[-1]

def get_local_repo_url():
    repo = git.Repo(".")
    origin = repo.remotes.origin
    return origin.url

def create_tag(repo, tag_num):
    repo.index.add(['metadata.rb'])
    repo.index.commit('Tagging for %s' % tag_num)
    repo.create_tag('v' + tag_num)

def commit_and_push(repo, name):
    try:
        print "Pushing %s..." % name
        tag = CookbookMetadata(".tina/" + name + "/metadata.rb").version
        if not tag == "0.0.0":
            create_tag(repo, tag)
            repo.remotes.origin.push('--tags')
    except git.GitCommandError as e:
        print ("Problem committing to '%s', error was '%s'" % (name, e.command))
        raise
