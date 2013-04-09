import unittest
from tina.version_requirement import VersionRequirement
from mock import Mock
from tina.tag import Tag

class TestVersionRequirement(unittest.TestCase):
    def test_version_requirement_init(self):
        dependence = "whatever"
        name = "test_project"
        operator = ">"
        VersionRequirement._store_version = Mock()

        req = VersionRequirement(dependence, name, operator, None)

        self.assertEquals(req.dependence, dependence)
        self.assertEquals(req.name, name)
        self.assertEquals(req.operator, operator)

    def test_store_version_eq(self):
        operator = "="
        version = "v1.2.3"
        expected_tag = Tag(version)
        req = VersionRequirement(None, None, operator, version)
        self.assertEquals(req.version, expected_tag)

    def test_store_version_gt(self):
        operator = ">"
        version = "v1.2.3"
        expected_tag = Tag(version)
        req = VersionRequirement(None, None, operator, version)
        self.assertEquals(req.version, expected_tag)

    def test_store_version_gt_eq(self):
        operator = ">="
        version = "v1.2.3"
        expected_tag = Tag(version)
        req = VersionRequirement(None, None, operator, version)
        self.assertEquals(req.version, expected_tag)

    def test_store_version_lt(self):
        operator = "<"
        version = "v1.2.3"
        self.assertRaises(Exception, VersionRequirement, None, None, 
                          operator, version)

    def test_store_version_with_one_num(self):
        operator = "~>"
        version = "v2"
        expected_tag = Tag("v2.0.0")
        expected_max_tag = Tag(
