from GitLib import *
from CookbookMetadata import *

class CookbookRepo:
    def __init__(self, url):
        self.url = url
        self.name = get_name_from_url(url)
        self.checkout()
        self.metadata = CookbookMetadata(".tina/" + self.name + "/metadata.rb")

    def checkout(self):
        print "Cloning " + self.name + "..."
        repo = checkout_repo(self.url)
        self.old_tag = get_tag_of_repo(repo)
        if self.old_tag:
            self.changed = self.changed_since_last_tag(repo)
        else:
            self.changed = False
        self.version_bump()

    def changed_since_last_tag(self, repo):
        master = repo.commit("master")
        last = repo.commit("v" + self.old_tag)
        return master.committed_date > last.committed_date

    def resolve_deps(self, versions):
        self.metadata.inject_versions(self.new_tag, versions)

    def commit(self):
        if self.old_tag != self.new_tag:
            commit_and_push(self.name, self.new_tag)

    def version_bump(self):
        if not self.old_tag:
            self.old_tag = "1.0.0"

        if self.changed:
            nums = self.old_tag.split(".")
            nums[-1] = str(int(nums[-1]) + 1)
            self.new_tag = ".".join(nums)
        else:
            self.new_tag = self.old_tag
