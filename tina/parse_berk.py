import re
from urlparse import urlparse
from subprocess import check_output
import json
from tag import Tag

def cookbooks_from_berks():
    print "Running berks install"
    data = check_output(["berks", "install", "--path", ".tina/berks", "--format=json"])
    cookbooks = json.loads(data)
    for cookbook in cookbooks["cookbooks"]:
        rw_url = None
        taggable = False
        if "location" in cookbook.keys():
            taggable = False
            url = get_url_from_string(cookbook["location"])
            rw_url = normalize_urls_to_git(url)
            if rw_url:
                regex = re.compile(r'.*rackspace.*')
                match = regex.match(rw_url)
                if match:
                    taggable = True
        else:
            cookbook["location"] = "Opscode"
                
        cookbook["rw_url"] = rw_url
        cookbook["taggable"] = taggable
        cookbook["tag"] = Tag(cookbook["version"])

    return cookbooks["cookbooks"]


#TODO: always fails if urls are already git@github.com:repo.git
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
