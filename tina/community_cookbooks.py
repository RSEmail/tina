from tina import * 
import urllib2
import json

def tag_compare(x, y):
    x_nums = x.split(".")
    y_nums = y.split(".")
    for (x,y) in zip(x_nums,y_nums):
        if x != y:
            return int(x) - int(y)
    return 0



class CommunityCookbooks:
    def __init__(self, cookbook_names):
        self.versions = {}
        for cookbook in cookbook_names:
            version = self.get_opscode_version(cookbook)
            if version:
                self.versions[cookbook] = version
                print ("Found community cookbook '%s': %s" % (cookbook, version))
        
    def get_opscode_version(self, cookbook):
        try:
            response = urllib2.urlopen("http://cookbooks.opscode.com/api/v1/cookbooks/" + cookbook)
            data = json.loads(response.read())
            versions = []
            for url in data["versions"]:
                version=url.encode('ascii','ignore').split("/")[-1].replace("_", ".")
                versions.append(version)
            versions.sort(cmp=tag_compare)
            newest = versions[-1]
            return newest 
        except urllib2.HTTPError as e: 
            if e.code == 404:
                return None
