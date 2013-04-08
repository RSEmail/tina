import unittest
from tina.tag import Tag
from mock import Mock

class TestTag(unittest.TestCase):

    def setUp(self):
        self.version_str = "v1.2.3"
        self.my_tag = Tag(self.version_str)

    def test_init(self):
        self.assertEquals(self.my_tag.pretext, "v")
        self.assertEquals(self.my_tag.major, 1)
        self.assertEquals(self.my_tag.minor, 2)
        self.assertEquals(self.my_tag.build, 3)

    def test_init_without_pretext(self):
        version_str_without_pretext = "1.2.3"
        my_tag = Tag(version_str_without_pretext)
        self.assertEquals(my_tag.pretext, "")
        self.assertEquals(my_tag.major, 1)
        self.assertEquals(my_tag.minor, 2)
        self.assertEquals(my_tag.build, 3)

    def test_init_malformed(self):
        bad_version_str = "1.2.v3"
        self.assertRaises(Exception, Tag, bad_version_str)

    def test_init_missing_build(self):
        bad_version_str = "v1.1."
        self.assertRaises(Exception, Tag, bad_version_str)


    def test_less_than_major(self):
        version_string_left = "v1.2.3"
        version_string_right = "v2.3.4"

        left_tag = Tag(version_string_left)
        right_tag = Tag(version_string_right)

        self.assertTrue(left_tag < right_tag)

    def test_less_than_minor(self):
        version_string_left = "v2.2.2"
        version_string_right = "2.4.9"

        left_tag = Tag(version_string_left)
        right_tag = Tag(version_string_right)

        self.assertTrue(left_tag < right_tag)

    def test_less_than_build(self):
        version_string_left = "2.2.2"
        version_string_right = "v2.2.3"

        left_tag = Tag(version_string_left)
        right_tag = Tag(version_string_right)

        self.assertTrue(left_tag < right_tag)


    def test_repr(self):
        output = self.my_tag.__repr__()
        expected = self.version_str
        self.assertEquals(output, expected)


    def test_version_str(self):
        output = self.my_tag.version_str()
        expected = "1.2.3"
        self.assertEquals(expected, output)


    def test_build_bump(self):
        self.my_tag.build_bump()
        self.assertEquals("1.2.4", self.my_tag.version_str())

    def test_minor_bump(self):
        self.my_tag.minor_bump()
        self.assertEquals("1.3.0", self.my_tag.version_str())

    def test_major_bump(self):
        self.my_tag.major_bump()
        self.assertEquals("2.0.0", self.my_tag.version_str())

    def test_multi_bump(self):
        self.my_tag.major_bump()
        for i in range(3):
            self.my_tag.minor_bump()
        for i in range(6):
            self.my_tag.build_bump()
        expected = "v2.3.6"
        output = self.my_tag.__repr__()
        self.assertEquals(output, expected)
