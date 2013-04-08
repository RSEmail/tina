import unittest
import tina.berkslib
import json
from mock import Mock

class TestParseBerk(unittest.TestCase):
    def test_get_name_from_url(self):
        repo_url = "http://github.com/test_project.git"
        output = tina.berkslib.get_name_from_url(repo_url)
        expected = "test_project"
        self.assertEquals(expected, output)

    def test_get_name_from_url_no_match(self):
        repo_url = "http://github.com/test_bad_proj.gat"
        self.assertRaises(Exception, tina.berkslib.get_name_from_url, repo_url)

    def test_get_name_from_url_extra_extension(self):
        repo_url = "http://github.com/test_weird_proj.git.png.jpeg"
        output = tina.berkslib.get_name_from_url(repo_url)
        expected = "test_weird_proj"
        self.assertEquals(output, expected)


    def test_repos_from_berks(self):
        json_string = """
        {
            "cookbooks": [
                {
                    "name": "sudo",
                    "version": "2.0.4"
                },
                {
                    "location": "git: 'git://github.com/test_project.git'",
                    "name": "test_project",
                    "version": "1.33.7"
                }
            ]
        }"""
        berks_json = json.loads(json_string)
        tina.berkslib._get_json_from_berks_run = Mock(return_value=berks_json)

        output = tina.berkslib.repos_from_berks()
        expected = {}
        expected["sudo"] = None
        expected["test_project"] = "git://github.com/test_project.git"
        self.assertEquals(expected, output)


    def test_get_url_from_string(self):
        line = "git: 'git://github.com/test_project.git'"
        output = tina.berkslib._get_url_from_string(line)
        expected = "git://github.com/test_project.git"
        self.assertEquals(expected, output)

    def test_get_url_from_string_no_match(self):
        line = "git://github.com/test_project.git"
        output = tina.berkslib._get_url_from_string(line)
        expected = None
        self.assertEquals(expected, output)

    def test_get_url_from_string_from_https(self):
        line = "https: 'https://github.com/test_project.git'"
        output = tina.berkslib._get_url_from_string(line)
        expected = "https://github.com/test_project.git"
        self.assertEquals(expected, output)

    def test_get_url_from_string_from_ssh(self):
        line = "ssh: 'ssh://github.com:test_project.git'"
        output = tina.berkslib._get_url_from_string(line)
        expected = "ssh://github.com:test_project.git"
        self.assertEquals(expected, output)


    def test_normalize_urls_to_git_no_url(self):
        url = None
        output = tina.berkslib.normalize_urls_to_git(url)
        expected = None
        self.assertEquals(expected, output)

    def test_normalize_urls_to_git_ssh(self):
        url = "git@github.com:test_project.git"
        output = tina.berkslib.normalize_urls_to_git(url)
        expected = "git@github.com:test_project.git"
        self.assertEquals(expected, output)

    def test_normalize_urls_to_git_malformed(self):
        url = "git@github.com/test_project.git"
        self.assertRaises(SyntaxError, tina.berkslib.normalize_urls_to_git, url)

    def test_normalize_urls_to_git_from_https(self):
        url = "https://github.com/test_project.git"
        output = tina.berkslib.normalize_urls_to_git(url)
        expected = "git@github.com:test_project.git"
        self.assertEquals(expected, output)

    def test_normalize_urls_to_git_from_git(self):
        url = "git://github.com/test_project.git"
        output = tina.berkslib.normalize_urls_to_git(url)
        expected = "git@github.com:test_project.git"
        self.assertEquals(expected, output)

    def test_normalize_urls_to_git_from_weirdness(self):
        url = "blarg+-://@github.com/test_project"
        output = tina.berkslib.normalize_urls_to_git(url)
        expected = "git@github.com:test_project.git"
        self.assertEquals(expected, output)
