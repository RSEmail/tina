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

    def __gt__(self, other):
        if self.major != other.major:
            return self.major > other.major
        elif self.minor != other.minor:
            return self.minor > other.minor
        else:
            return self.build > other.build

    def __eq__(self, other):
        return (self.major == other.major and
                self.minor == other.minor and
                self.build == other.build)

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return self < other or self == other

    def __ge__(self, other):
        return self > other or self == other

    def __repr__(self):
        return "%s%d.%d.%d" % (self.pretext, self.major, self.minor,
            self.build)

    def version_str(self):
        return "%d.%d.%d" % (self.major, self.minor, self.build)

    def build_bump(self):
        self.build = self.build + 1

    def minor_bump(self):
        self.minor = self.minor + 1
        self.build = 0

    def major_bump(self):
        self.major = self.major + 1
        self.minor = 0
        self.build = 0
