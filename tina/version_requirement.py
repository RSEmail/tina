from tag import Tag

class VersionRequirement:
    def __init__(self, dependence, name, operator, version):
        self.dependence = dependence
        self.name = name
        self.operator = operator
        self.max_version = None
        self.store_version(version)

    def store_version(self, version):
        op = self.operator
        if op == "=" or op == ">" or op == ">=":
            self.version = Tag(version)
        elif op == "~>":
            version_nums = version.split(".")
            while len(version_nums) < 3:
                version_nums.append("0")
            self.version = Tag(".".join(version_nums))
            version_nums[0] = str(int(version_nums[0]) + 1)
            self.max_version = Tag(".".join(version_nums))
        else:
            raise Exception("Error: unknown dependence operator: %s" % operator)

    def compatible_with(self, other):
        if self.operator == "=":
            if other.operator == "=":
                return self.version == other.version
            elif other.operator == ">=":
                return self.version >= other.version
            elif other.operator == ">" or other.operator == "~>":
                return self.version > other.version
        elif self.operator == "~>":
            return (other.version >= self.version and
                    other.version < self.max_version)
        elif self.operator == ">":
            if other.operator == ">" or other.operator == ">=":
                return True
            elif other.operator == "=":
                return other.version > self.version
            elif other.operator == "~>":
                return (self.version > other.version and
                        self.version < other.max_version)
        elif self.operator == ">=":
            if other.operator == ">" or other.operator == ">=":
                return True
            elif other.operator == "=":
                return other.version >= self.version
            elif other.operator == "~>":
                return (self.version >= other.version and
                        self.version < other.max_version)
