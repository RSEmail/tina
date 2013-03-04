import unittest
import ParseBerk

class TestParseBerk(unittest.TestCase):
    def test_normalize_urls_to_git(self):
        urls = ["git://github.com/tina.git"]
        normalized = ParseBerk.normalize_urls_to_git(urls)
        
        expected = ["git@github.com:tina.git"]
        self.assertEquals(normalized, expected)

    def test_normalize_urls_to_git_multiple_urls(self):
        urls = ["git://github.com/tina.git", "git://github.pants.com/pants/myrepo.git"]
        normalized = ParseBerk.normalize_urls_to_git(urls)
        
        expected = ["git@github.com:tina.git", "git@github.pants.com:pants/myrepo.git"]
        self.assertEquals(normalized, expected)

    def test_normalize_urls_to_git_without_git(self):
        urls = ["git://github.com/tina", "git://github.pants.com/pants/myrepo"]
        normalized = ParseBerk.normalize_urls_to_git(urls)
        
        expected = ["git@github.com:tina.git", "git@github.pants.com:pants/myrepo.git"]
        self.assertEquals(normalized, expected)

    def test_normalize_urls_to_git_https(self):
        urls = ["https://github.com/tina", "https://github.pants.com/pants/myrepo"]
        normalized = ParseBerk.normalize_urls_to_git(urls)
        
        expected = ["git@github.com:tina.git", "git@github.pants.com:pants/myrepo.git"]
        self.assertEquals(normalized, expected)

    # def test_normalize_urls_to_git_at(self):
    #     urls = ["git@github.com/tina", "git@github.pants.com/pants/myrepo"]
    #     normalized = ParseBerk.normalize_urls_to_git(urls)
    #     
    #     expected = ["git@github.com:tina.git", "git@github.pants.com:pants/myrepo.git"]
    #     self.assertEquals(normalized, expected)

    def test_normalize_urls_to_git_malforned_url(self):
        urls = ["asdgasd.asdlkjh@laksjd.asd//alskdj"]
        self.assertRaises(SyntaxError, ParseBerk.normalize_urls_to_git, urls)

