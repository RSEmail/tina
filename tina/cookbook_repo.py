import copy
import git
import shutil
from cookbook_metadata import *
from gitlib import *

class CookbookRepo:
    def __init__(self, repo_name, url=None, checkout=False):
        self.repo_name = repo_name
        self.url = url
        self.changed = False
        self.using_git = False
        if checkout and url:
            self.using_git = True 
            if os.path.exists(".tina/" + repo_name):
                shutil.rmtree(".tina/" + repo_name)
            self.checkout()
        else:
            self.repo = git.Repo(".tina/" + self.repo_name)
        self.metadata = CookbookMetadata(".tina/" + self.repo_name + "/metadata.rb")
        self.set_tag()

    def checkout(self):
        self.repo = checkout_repo(repo_name, self.url)

    def set_tag(self):
        if self.using_git:
            self.old_tag = get_tag_of_repo(self.repo)
            if self.old_tag:
                self.changed = self.changed_since_last_tag(self.repo)
                self.version_bump()
        else:
            self.old_tag = self.metadata.version
            self.new_tag = self.old_tag

    def changed_since_last_tag(self, repo):
        master = repo.commit("master")
        last = repo.commit(str(self.old_tag))
        return master.committed_date > last.committed_date

    def resolve_deps(self, versions):
        if self.changed:
            self.metadata.inject_versions(self.new_tag, versions)

    def commit(self):
        if self.changed:
            commit_and_push(self.repo, self.repo_name, self.new_tag)

    def version_bump(self):
        if self.changed:
            self.new_tag = copy.copy(self.old_tag)
            self.new_tag.build_bump()
        else:
            self.new_tag = self.old_tag
