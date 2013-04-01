import re
from urlparse import urlparse
from subprocess import check_output
import json
from tag import Tag

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)


def repos_from_berks():
    print "Running berks install"
    berks_output = check_output(["berks", "install", "--path", ".tina", "--format=json"])
    data = json.loads(berks_output)
    print data
    repos = {}
    for repo in data["cookbooks"]:
        url = None
        if "location" in repo.keys():
            url = get_url_from_string(repo["location"])
            if url:
                rw_url = normalize_urls_to_git(url)
                if rw_url:
                    url = rw_url
        if url:
            name = get_name_from_url(url)
        else:
            name = repo["name"]
        repos[name] = url
    return repos


def normalize_urls_to_git(url):
    if url == None:
        return None
    parts = urlparse(url)
    if not parts.hostname or not parts.path:
        raise SyntaxError("URL is malformed: '%s'" % url)
    norm = "git@" + parts.hostname
    norm += ":" + parts.path.lstrip("/")
    if not norm.endswith(".git"):
        norm += ".git"
    return norm

def get_url_from_string(line):
    regex = re.compile(r'.*[\'\"]([a-zA-Z]*://.*?)[\'\"]')
    match = regex.match(line)
    if not match:
        return None
    word = match.group(1)
    return (word.replace('\"',''))
