import copy
import git
import os
import re

import config
import tag
import util

class CookbookRepo:
    def __init__(self, repo_name, repo, remote=None):
        self.name = repo_name
        self.repo = repo
        self.remote = remote
        self.is_main_repo = False

        self.latest_tag = self.get_latest_tag()
        self.new_tag = None

        self.changed = self.changed_since_last_tag()
        self.needs_to_bump = self.changed

    @staticmethod
    def _checkout_repo(repo_name, repo_url):
        #print 'Cloning {0}...'.format(repo_name)
        local_path = os.path.join('.tina', repo_name)
        util.rmdir(local_path)

        return git.Repo.clone_from(repo_url, local_path)

    @staticmethod
    def search_for_repo(repo_name):
        user = config.TinaConfig.git_user
        url = config.TinaConfig.git_url
        orgs = config.TinaConfig.git_orgs

        repos = ['{0}@{1}:{2}'.format(user, url, org) for org in orgs]

        target_dir = os.path.join('.tina', repo_name)
        for repo in repos:
            try:
                repo_url = '{0}/{1}.git'.format(repo, repo_name)
                repo = git.Repo.clone_from(repo_url, target_dir)
                return CookbookRepo(repo_name, repo, remote=repo_url)
            except Exception as e:
                continue

        raise ValueError('Could not find repo: {0}'.format(repo_name))

    @classmethod
    def get_cookbook_repo(cls, name, location):
        repo = cls._checkout_repo(name, location)
        return CookbookRepo(name, repo)

    def reclone(self):
        self._checkout_repo(self.name, self.remote)

    def get_latest_tag(self):
        tag_re = re.compile('^[a-zA-Z]*\d+\.\d+\.\d+$')
        tags = self.repo.tags
        tag_list = [tag.Tag(str(t)) for t in tags if tag_re.match(str(t))]

        if len(tag_list) == 0:
            return None
        else:
            return sorted(tag_list)[-1]

    def get_tag(self):
        return self.new_tag if self.needs_to_bump else self.latest_tag

    def changed_since_last_tag(self):
        if not self.latest_tag:
            return True

        master = self.repo.commit('master')
        last = self.repo.commit(str(self.latest_tag))
        return last.parents[0] != master

    def commit(self):
        if self.needs_to_bump:
            version = str(self.new_tag)
            print 'Pushing {0} ({1})...'.format(self.name, version)

            self.repo.index.add(['metadata.rb'])
            try:
                self.repo.index.commit('Tag for {0}'.format(version))
            except Exception:
                pass
            self.repo.create_tag(version)
            self.repo.remotes.origin.push('--tags')

    def bump_version(self, level=1):
        if self.needs_to_bump:
            if self.latest_tag:
                self.new_tag = copy.copy(self.latest_tag)
                if level == 1:
                    self.new_tag.build_bump()
                elif level == 2:
                    self.new_tag.minor_bump()
                elif level == 3:
                    self.new_tag.major_bump()
            else:
                self.new_tag = Tag('v0.0.1')
        else:
            self.new_tag = self.old_tag

    def unbump(self):
        self.needs_to_bump = False
        self.new_tag = None

    def __repr__(self):
        return 'CookbookRepo({0})'.format(self.name)

    def __cmp__(self, other):
        return cmp(self.name, other.name)
