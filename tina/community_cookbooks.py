import json
import urllib2
from tag import Tag

class CommunityCookbooks:
    def __init__(self, cookbook_names):
        self.versions = {}
        for cookbook in cookbook_names:
            version = self.get_opscode_version(cookbook)
            if version:
                self.versions[cookbook] = version
        
    def get_opscode_version(self, cookbook):
        try:
            response = urllib2.urlopen("http://cookbooks.opscode.com/api/v1/cookbooks/" + cookbook)
            data = json.loads(response.read())
            versions = []
            for url in data["versions"]:
                version=url.encode('ascii','ignore').split("/")[-1].replace("_", ".")
                versions.append(Tag(version))
            versions.sort()
            newest = versions[-1]
            return str(newest)
        except urllib2.HTTPError as e: 
            if e.code == 404:
                return None
