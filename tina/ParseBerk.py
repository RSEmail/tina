import re
from urlparse import urlparse

def get_git_urls_from_file(filename):
    urls = get_urls_from_file(filename)
    return normalize_urls_to_git(urls)

#TODO: always fails if urls are already git@github.com:repo.git
def normalize_urls_to_git(urls):
    normalized_urls = []
    for url in urls:
        parts = urlparse(url)
        if not parts.hostname  or not parts.path:
            raise SyntaxError("URL is malformed: '%s'" % url)
        norm = "git@" + parts.hostname
        norm += ":" + parts.path.lstrip("/")
        if not norm.endswith(".git"):
            norm += ".git"
        normalized_urls.append(norm)
    return normalized_urls

def get_urls_from_file(filename):
    urls = []
    try:
        raw = open(filename, "r")
        regex = re.compile(r'"[a-zA-Z]*://.*?"')
        for line in raw:
            matches = regex.findall(line)
            for word in matches:
                urls.append(word.replace('\"',''))
    except IOError as e:
        print "Unable to open file to parse it '{0}': '{1}'".format(filename, e.strerror)
        raise
    else:
        raw.close()
    return urls
