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
    data = _get_json_from_berks_run()
    locations = _get_locations_from_berks_list()
    repos = {}
    for repo in data["cookbooks"]:
        url = None
        if "location" in repo.keys():
            url = _get_url_from_string(repo["location"])
        elif locations.has_key(repo['name']):
            url = locations[repo['name']]
        # name is the local_dir the repo was checked out into
        repos[repo["name"]] = url
    return repos

def _get_json_from_berks_run():
    print "Running Berkshelf..."
    proc = subprocess.Popen(["berks", "vendor", ".tina", 
        "--format=json"], stdout=subprocess.PIPE)
    berks_output, errors = proc.communicate()
    return json.loads(berks_output)

def _get_locations_from_berks_list():
    locations = {}
    proc = subprocess.Popen(["berks", "list"], stdout=subprocess.PIPE)
    for line in proc.stdout:
        line = line.strip()
        if not line.startswith('*') or not 'from' in line or\
            'github' not in line:
            continue
        line_parts = line.split('from')
        cookbook_part = line_parts[0]
        cookbook = cookbook_part.split(' ')[1]
        source_part = line_parts[1].strip()
        url = source_part.split(' ')[0].strip()
        locations[cookbook] = url
    return locations

def _get_url_from_string(line):
    regex = re.compile(".*['\"]((https://|git://|git@).*?)['\"]")
    match = regex.match(line)
    if not match:
        return None
    word = match.group(1)
    return (word.replace("\"",""))

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

