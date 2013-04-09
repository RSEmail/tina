import unittest
from tina.cookbook_metadata import CookbookMetadata
import json

class TestCookbookMetadata(unittest.TestCase):
    def test_cookbook_metadata_init(self):
        local_dir = "test_project"

