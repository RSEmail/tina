import copy
import git
from cookbook_metadata import *
from gitlib import *

class CookbookRepo:
    def __init__(self, name, url=None):
        self.name = name
        if url:
            self.url = url
            self.checkout()
        else:
            self.repo = git.Repo(".tina/" + self.name)
        self.metadata = CookbookMetadata(".tina/" + self.name + "/metadata.rb")

    def checkout(self):
        self.repo = checkout_repo(self.url)
        self.old_tag = get_tag_of_repo(self.repo)
        if self.old_tag:
            self.changed = self.changed_since_last_tag(self.repo)
        else:
            self.changed = False
        self.version_bump()

    def changed_since_last_tag(self, repo):
        master = repo.commit("master")
        last = repo.commit(str(self.old_tag))
        return master.committed_date > last.committed_date

    def resolve_deps(self, versions):
        if self.changed:
            self.metadata.inject_versions(self.new_tag, versions)

    def commit(self):
        if self.changed:
            commit_and_push(self.repo, self.name, self.new_tag)

    def version_bump(self):
        if self.changed:
            self.new_tag = copy.copy(self.old_tag)
            self.new_tag.build_bump()
        else:
            self.new_tag = self.old_tag
