import re
import sys

class Tag:
    def __init__(self, version_str):
        match = re.match('(\D*)(\d+)\.(\d+)\.(\d+)', version_str)
        if not match:
            raise Exception('Error: malformed tag: {0}'.format(version_str))
        self.prefix = match.group(1)
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

    def __str__(self):
        return '{0}{1}'.format(self.prefix, self.version_str())

    def __repr__(self):
        return 'Tag({0})'.format(str(self))

    def version_str(self):
        return '{0}.{1}.{2}'.format(self.major, self.minor, self.build)

    def build_bump(self):
        self.build = self.build + 1

    def minor_bump(self):
        self.minor = self.minor + 1
        self.build = 0

    def major_bump(self):
        self.major = self.major + 1
        self.minor = 0
        self.build = 0

    def increment(self):
        self.build_bump()

    def decrement(self):
        self.build = self.build - 1
        if self.build < 0:
            self.build = sys.maxint
            self.minor = self.minor - 1
            if self.minor < 0:
                self.minor = sys.maxint
                self.major = self.major - 1

    @staticmethod
    def max_tag():
        t = Tag('0.0.0')
        t.major = sys.maxint
        t.minor = sys.maxint
        t.build = sys.maxint
        return t

    @staticmethod
    def min_tag():
        return Tag('0.0.0')
