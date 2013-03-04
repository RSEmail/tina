import re

class CookbookMetadata:
    def __init__(self, filename):
        self.filename = filename
        self.cookbook_name = None
        self.depends = []
        self.parse_metadata();

    def parse_metadata(self):
        try:
            raw = open(self.filename, "r")
            regex_name = re.compile(r'name\s+"(.*?)"')
            regex_depends = re.compile(r'depends\s+"(.*?)"')
            for line in raw:
                matches = regex_name.findall(line)
                for word in matches:
                    if self.cookbook_name:
                        raise Exception("Metadata file has multiple 'name' "
                                        "sections: '%s'" % self.filename)
                    self.cookbook_name = word
                matches = regex_depends.findall(line)
                for word in matches:
                    self.depends.append(word)
        except IOError as e:
            print "Unable to open file to parse it '{0}': '{1}'".format(self.filename, e.strerror)
            raise
        else:
            raw.close()
        return 

    def inject_versions(self, tagged_version, versions):
        metadata = open(self.filename, "r")
        content = metadata.readlines()
        metadata.close()

        regex_depends = re.compile(r'depends\s+"(.*?)"')
        regex_version = re.compile(r'version\s+"(.*?)"')
        new_content = []
        for line in content:
            version_match = regex_version.match(line)
            if version_match:
                line = line.replace(version_match.group(1), tagged_version)

            depends_match = regex_depends.match(line)
            if depends_match:
                cookbook = depends_match.group(1)
                if not cookbook in versions:
                    raise Exception("Missing version number for cookbook '%s' "
                                    % cookbook)
                else:
                    version = versions[cookbook]
                    line = line.replace(r'"%s"' % cookbook,
                                        r'"%s", "= %s"' % (cookbook, version))
            new_content.append(line)

        metadata = open(self.filename, "w")
        metadata.write("".join(new_content))
        metadata.close()
        

if __name__ == "__main__":
    filename = "metadata.rb"
    metadata = CookbookMetadata(filename)
    versions = {"tina": "1.0.1", "test_tina": "2.0.2", "yum": "3.0.0"}
    metadata.inject_versions(versions)

