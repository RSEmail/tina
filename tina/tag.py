import re

class Tag:
    def __init__(self, version_str):
        match = re.match(r"(\D*)(\d+)\.(\d+)\.(\d+)", version_str)
        if not match:
            raise Exception("Error: malformed tag: " + version_str)
        self.pretext = match.group(1)
        self.major = int(match.group(2))
        self.minor = int(match.group(3))
        self.build = int(match.group(4))

    def __lt__(self, other):
        if self.major != other.major:
            return self.major < other.major
        elif self.minor != other.minor:
            return self.minor < other.minor
        else:
            return self.build < other.build

    def __repr__(self):
        return "%s%d.%d.%d" % (self.pretext, self.major, self.minor, self.build)

    def build_bump(self):
        self.build = self.build + 1

    def minor_bump(self):
        self.minor = self.minor + 1

    def major_bump(self):
        self.major = self.major + 1
