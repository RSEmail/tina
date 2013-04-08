import sys
from tag import Tag

class VersionRequirement:
    def __init__(self, dependence, name, operator, version):
        self.dependence = dependence
        self.name = name
        self.operator = operator
        self.version = version
        self.store_versions()

    def store_versions(self):
        op = self.operator
        if op == "=":
            self.min_version = Tag(self.version)
            self.max_version = Tag(self.version)
        elif op == ">":
            self.min_version = Tag(self.version)
            self.min_version.increment()
            self.max_version = Tag.max_tag()
        elif op == ">=":
            self.min_version = Tag(self.version)
            self.max_version = Tag.max_tag()
        elif op == "<":
            self.min_version = Tag.min_tag()
            self.max_version = Tag(self.version)
            self.max_version.decrement()
        elif op == "<=":
            self.min_version = Tag.min_tag()
            self.max_version = Tag(self.version)
        elif op == "~>":
            version_nums = self.version.split(".")
            length = len(version_nums)
            while len(version_nums) < 3:
                version_nums.append("0")
            version_str = ".".join(version_nums)

            self.min_version = Tag(version_str)
            if length == 1:
                self.max_version = Tag.max_tag()
            else:
                self.max_version = Tag(version_str)
                if length == 2: self.max_version.major_bump()
                elif length == 3: self.max_version.minor_bump()
                self.max_version.decrement()
        else:
            raise Exception("Error: unknown version constraint: %s" % operator)

    def compatible_with(self, other):
        return ((self.min_version <= other.max_version) and
                (self.max_version >= other.min_version))
