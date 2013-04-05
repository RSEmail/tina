import re
from urlparse import urlparse
import subprocess
import json
from tag import Tag

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)


def repos_from_berks():
    print "Running berks install"
    proc = subprocess.Popen(["berks", "install", "--path", ".tina", 
        "--format=json"], stdout=subprocess.PIPE)
    berks_output, errors = proc.communicate()
    data = json.loads(berks_output)
    repos = {}
    for repo in data["cookbooks"]:
        url = None
        if "location" in repo.keys():
            url = get_url_from_string(repo["location"])
        # name is the local_dir the repo was checked out into
        repos[repo["name"]] = url
    return repos

def normalize_urls_to_git(url):
    if url == None:
        return None
    if re.match("git@.*:.*", url):
        return url
    parts = urlparse(url)
    if not parts.hostname or not parts.path:
        raise SyntaxError("URL is malformed: '%s'" % url)
    norm = "git@" + parts.hostname
    norm += ":" + parts.path.lstrip("/")
    if not norm.endswith(".git"):
        norm += ".git"
    return norm

def get_url_from_string(line):
    regex = re.compile(".*[\'\"]([a-zA-Z]*://.*?)[\'\"]")
    match = regex.match(line)
    if not match:
        return None
    word = match.group(1)
    return (word.replace("\"",""))
