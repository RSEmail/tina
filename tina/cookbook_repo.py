import copy
from cookbook_metadata import *
from gitlib import *

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)

class CookbookRepo:
    def __init__(self, url):
        self.url = url
        self.name = get_name_from_url(url)
        self.checkout()
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
        if self.old_tag != self.new_tag:
            self.metadata.inject_versions(self.new_tag, versions)

    def commit(self):
        if self.old_tag != self.new_tag:
            commit_and_push(self.repo)

    def version_bump(self):
        if self.changed:
            self.new_tag = copy.copy(self.old_tag)
            self.new_tag.build_bump()
        else:
            self.new_tag = self.old_tag
