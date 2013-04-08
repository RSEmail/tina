import unittest
import tina.gitlib
from mock import Mock
import git

class TestGitlib(unittest.TestCase):
    def test_checkout_repo(self):
        git.Repo.clone_from = Mock(return_value='test')
        repo_name = "test_project"
        repo_url = "git://github.com/test_project.git"
        tina.gitlib.checkout_repo(repo_name, repo_url)
        git.Repo.clone_from.assert_called_with(repo_url, ".tina/test_project")

    def test_tag_of_repo_no_tags(self):
        repo = git.Repo
        repo.tags = []
        output = tina.gitlib.get_tag_of_repo(repo)
        expected = None
        self.assertEquals(expected, output)

    #def test_tag_of
        
