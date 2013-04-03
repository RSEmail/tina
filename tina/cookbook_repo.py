import copy
import git
import shutil
from cookbook_metadata import *
from berkslib import *
from gitlib import *

class CookbookRepo:
    def __init__(self, local_dir, url=None, force_checkout=False):
        self.local_dir = local_dir
        self.url = None
        if url:
            self.url = normalize_urls_to_git(url)
        self.changed = False
        self.using_git = False
        self.refresh_metadata()

    def checkout(self):
        if self.url:
            path = os.path.join(".tina", self.local_dir)
            if os.path.exists(path):
                shutil.rmtree(path)
            self.using_git = True
            self.repo = checkout_repo(self.local_dir, self.url)
            self.refresh_metadata()

    def refresh_metadata(self):
        self.metadata = CookbookMetadata(self.local_dir)
        self.name = self.metadata.cookbook_name
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
            commit_and_push(self.repo, self.local_dir, self.new_tag)

    def version_bump(self, level=1):
        if self.changed:
            self.new_tag = copy.copy(self.old_tag)
            if level == 1:
                self.new_tag.build_bump()
            elif level == 2:
                self.new_tag.minor_bump()
            elif level == 3:
                self.new_tag.major_bump()
        else:
            self.new_tag = self.old_tag
