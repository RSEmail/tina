import os
import re
from tag import Tag
from version_requirement import VersionRequirement

class CookbookMetadata:
    def __init__(self, local_dir):
        # The cookbook name will default to the local directory name,
        # since we can't guarantee community cookbooks will have the
        # name in the metadata file.
        self.cookbook_name = local_dir
        self.filename = os.path.join(".tina", local_dir, "metadata.rb")
        self.version = None
        self.depends = []
        self.requirements = {}
        self.parse_metadata();

    def parse_metadata(self):
        try:
            raw = open(self.filename, "r")
            regex_name = re.compile("name\s+[\'\"](.*?)[\'\"]")
            regex_depends = re.compile("depends\s+[\'\"](.*?)[\'\"]"
                "(,\s*[\'\"]([~<>=]+)\s+([\d\.]+)[\'\"])?")
            regex_version = re.compile("version\s+[\'\"](.*?)[\'\"]")
            for line in raw:
                # Find the name of the cookbook.
                matches = regex_name.findall(line)
                for word in matches:
                    self.cookbook_name = word

                # Find the list of dependencies.
                match = regex_depends.match(line)
                if match:
                    name = match.group(1)
                    self.depends.append(name)
                    if match.group(2):
                        operator = match.group(3)
                        version = match.group(4)
                        self.requirements[name] = VersionRequirement(self.cookbook_name, name, operator, version)

                # Find the current version of the cookbook.
                matches = regex_version.match(line)
                if matches:
                    if self.version:
                        raise Exception("Metadata file has multiple 'version' "
                            "sections: '%s'" % self.filename)
                    self.version = Tag(matches.group(1))

        except IOError as e:
            print "Unable to open file to parse it '{0}': " \
                "'{1}'".format(self.filename, e.strerror)
            raise
        else:
            raw.close()
        return 

    def inject_versions(self, tag, versions):
        metadata = open(self.filename, "r")
        content = metadata.readlines()
        metadata.close()

        regex_depends = re.compile("depends\s+[\'\"](.*?)[\'\"]")
        regex_version = re.compile("version\s+[\'\"](.*?)[\'\"]")
        new_content = []
        for line in content:
            version_match = regex_version.match(line)
            if version_match:
                line = line.replace(version_match.group(1), tag.version_str())

            depends_match = regex_depends.match(line)
            if depends_match:
                cookbook = depends_match.group(1)
                if not cookbook in versions:
                    raise Exception("Missing version number for cookbook '%s' "
                                    % cookbook)
                else:
                    version = versions[cookbook].version_str()
                    line = re.sub("[\'\"]%s[\'\"]" % cookbook,
                        "\"%s\", \"= %s\"" % (cookbook, version), line)
            new_content.append(line)

        metadata = open(self.filename, "w")
        metadata.write("".join(new_content))
        metadata.close()
