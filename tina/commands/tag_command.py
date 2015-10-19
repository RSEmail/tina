import json
import logging
import optparse
import os
import re
import sys

from ..cookbook_repo import CookbookRepo
from .. import util

class Node(object):
    def __init__(self, obj):
        self.obj = obj
        self.visited = False
        self.dependencies = []

class TagCommand(object):
    def __init__(self):
        self.cleanup = True

        self.parser = optparse.OptionParser(usage='tina tag <cookbook> [options]')
        self.parser.add_option('-v', '--verbose',
                               action='store_true',
                               dest='verbose',
                               help='enable verbose logging')
        self.parser.add_option('-q', '--quiet',
                               action='store_true',
                               dest='quiet',
                               help='disable all logging except errors')
        self.parser.add_option('-n', '--no-cleanup',
                               action='store_true',
                               dest='no_cleanup',
                               help='leave temporary files after finishing')

    @staticmethod
    def _get_local_repos(local_cookbooks):
        repos = []
        for name, location in local_cookbooks.iteritems():
            repos.append(CookbookRepo.get_cookbook_repo(name, location))

        return repos

    @staticmethod
    def _parse_metadata_rb_dependencies(metadata_file):
        dependencies = []
        with open(metadata_file) as fp:
            depends_re = re.compile('^depends\s+[\'\"]([^\'\"]+)[\'\"]'
                                    '(,\s*[\'\"][^\'\"]+[\'\"])?')
            for line in fp:
                match = depends_re.match(line)
                if match:
                    dependencies.append(match.group(1))

        return dependencies

    @staticmethod
    def _parse_metadata_json_dependencies(metadata_file):
        with open(metadata_file) as fp:
            metadata = json.load(fp)
            return metadata['dependencies'].keys()

    @classmethod
    def _get_metadata_dependencies(cls, repo_name):
        metadata_rb_file = os.path.join('.tina', repo_name, 'metadata.rb')
        metadata_json_file = os.path.join('.tina', repo_name, 'metadata.json')

        if os.path.isfile(metadata_rb_file):
            return cls._parse_metadata_rb_dependencies(metadata_rb_file)
        elif os.path.isfile(metadata_json_file):
            return cls._parse_metadata_json_dependencies(metadata_json_file)
        else:
            raise Exception('Could not find a metadata file to parse')

    @staticmethod
    def _update_cookbooks(cookbook, repo_version, versions):
        metadata_file = os.path.join('.tina', cookbook.name, 'metadata.rb')
        version_re = re.compile('(version\s+)([\'\"])[^\'\"]+[\'\"]')
        depends_re = re.compile('(depends\s+)([\'\"])([^\'\"]+)[\'\"]')
        new_file = []

        with open(metadata_file) as f:
            for line in f:
                version_match = version_re.match(line)
                if version_match:
                    prefix = version_match.group(1)
                    quote = version_match.group(2)
                    version = str(repo_version)
                    version_line = '{0}{1}{2}{1}\n'.format(prefix, quote, version)
                    new_file.append(version_line)
                    continue

                depends_match = depends_re.match(line)
                if depends_match:
                    prefix = depends_match.group(1)
                    quote = depends_match.group(2)
                    name = depends_match.group(3)
                    version = versions[name]
                    line = '{0}{1}{2}{1}, {1}= {3}{1}\n'.format(prefix, quote,
                        name, version)
                    new_file.append(line)
                    continue

                new_file.append(line)

        with open(metadata_file, 'w') as f:
            f.write(''.join(new_file))

        cookbook.commit()

    @classmethod
    def _mark_repo_and_dependencies(cls, graph, repo_name):
        node = graph[repo_name]
        if node.visited:
            return

        node.visited = True
        node.obj.needs_to_bump = True
        for name in node.dependencies:
            cls._mark_repo_and_dependencies(graph, name)

    @classmethod
    def _mark_repos_to_bump(cls, repo_list):
        graph = {}
        for repo in repo_list:
            n = Node(repo)
            graph[repo.name] = Node(repo)

        for repo in repo_list:
            dependencies = cls._get_metadata_dependencies(repo.name)
            for dependence in dependencies:
                if dependence in graph:
                    graph[dependence].dependencies.append(repo.name)

        for name, node in graph.iteritems():
            # Mark all nodes unvisited.
            for n in graph.values():
                n.visited = False

            repo = node.obj
            if repo.needs_to_bump:
                cls._mark_repo_and_dependencies(graph, name)

    @staticmethod
    def _print_cookbook_summary(repos):
        for i, cookbook in enumerate(repos, 1):
            if isinstance(cookbook, CookbookRepo):
                changed = '(*)' if cookbook.changed else ''
                main = '+' if cookbook.is_main_repo else ''
                base = '{0}. {1}{2}{3}'.format(i, main, cookbook.name, changed)
                if cookbook.needs_to_bump:
                    print '{0}: {1} -> {2}'.format(base, cookbook.latest_tag,
                                                   cookbook.new_tag)
                else:
                    print '{0}: unchanged'.format(base)
            else:
                name = cookbook[0]
                version = cookbook[1]
                print '{0}. {1}: {2}'.format(i, name, version)

    @classmethod
    def _gather_user_input(cls, repos):
        cls._print_cookbook_summary(repos)
        prompt = ('Enter a repository index to modify, "p" to print summary, '
                  '"c" to commit, and "a" to abort: ')
        while True:
            line = raw_input(prompt)
            if line == 'a':
                print 'Aborting without taking action'
                sys.exit(0)
            elif line == 'c':
                return
            elif line == 'p':
                cls._print_cookbook_summary(repos)
                continue

            try:
                n = int(line)
                if n < 1 or n > len(repos):
                    print 'Invalid repo index: {0}'.format(n)
                    continue

                repo = repos[n - 1]
                if isinstance(repo, CookbookRepo):
                    if repo.needs_to_bump:
                        cls._modify_changed_repo(repo)
                    else:
                        cls._modify_unchanged_repo(repo)
                else:
                    cls._modify_community_cookbook(repo)
            except ValueError:
                print 'Unrecognized option: {0}'.format(line)

    @staticmethod
    def _modify_changed_repo(repo):
        print '{0} will be tagged as {1}'.format(repo.name, repo.new_tag)
        print '1. Mark unchanged'
        print '2. Bump build number'
        print '3. Bump minor version'
        print '4. Bump major version'
        print '5. Do nothing'

        user_input = raw_input('Choose one of the above options: ')
        try:
            n = int(user_input)
            if n == 1:
                repo.unbump()
            elif n > 1 and n < 5:
                repo.bump_version(n - 1)
            elif n == 5:
                return
            else:
                print 'Unrecognized option: {0}'.format(user_input)
        except ValueError:
            print 'Unrecognized option: {0}'.format(user_input)

        if repo.needs_to_bump:
            print '{0} will now be tagged as {1}'.format(repo.name, repo.new_tag)
        else:
            print '{0} is now unchanged'.format(repo.name)

    @staticmethod
    def _modify_unchanged_repo(repo):
        print '{0} is unchanged and does not need to be tagged'.format(repo.name)
        print '1. Mark changed'
        print '2. Do nothing'

        user_input = raw_input('Choose one of the above options: ')
        try:
            n = int(user_input)
            if n == 1:
                repo.needs_to_bump = True
                repo.bump_version()
            elif n == 2:
                return
            else:
                print 'Unrecognized option: {0}'.format(user_input)
        except ValueError:
            print 'Unrecognized option: {0}'.format(user_input)

        if repo.changed:
            print '{0} will now be tagged as {1}'.format(repo.name, repo.new_tag)

    @staticmethod
    def _modify_community_cookbook(cookbook):
        name = cookbook[0]
        version = cookbook[1]
        print '{0} is a community cookbook, and will be pinned at {1}'.format(
            name, version)
        print '1. Modify pinned version'
        print '2. Do nothing'

        user_input = raw_input('Choose one of the above options: ')
        try:
            n = int(user_input)
            if n == 1:
                #repo.new_tag = Tag(raw_input('Enter new version: '))
                cookbook[1] = raw_input('Enter new version: ')
            elif n == 2:
                return
            else:
                print 'Unrecognized option: {0}'.format(user_input)
        except ValueError:
            print 'Unrecognized option: {0}'.format(user_input)

    @staticmethod
    def get_verb_name():
        return 'tag'

    def tag(self, tag_target):
        util.cleanup()

        try:
            logging.info('Locating the {0} repo'.format(tag_target))
            main_repo = CookbookRepo.search_for_repo(tag_target)
            main_repo.is_main_repo = True
        except ValueError as ve:
            logging.error('Error: {0}'.format(ve))
            sys.exit(1)

        berksfile_path = os.path.join('.tina', tag_target, 'Berksfile')
        try:
            logging.info('Running berks')
            berks_json = util.run_berks(berksfile_path)
        except ValueError:
            logging.error('Error: could not run berkshelf')
            sys.exit(1)

        # Clone again to override what berks placed.
        main_repo.reclone()
        cookbook_info = util.get_cookbook_information(berks_json)
        repo_list = self._get_local_repos(cookbook_info['local'])
        repo_list.append(main_repo)
        repo_list.sort()

        logging.info('Resolving dependencies')
        self._mark_repos_to_bump(repo_list)
        for repo in repo_list:
            if repo.needs_to_bump:
                repo.bump_version()

        self._gather_user_input(repo_list)

        if not main_repo.needs_to_bump:
            logging.info('{0} is not being tagged; exiting'.format(main_repo.name))
            sys.exit(0)

        versions = {}
        for cookbook in repo_list:
            versions[cookbook.name] = cookbook.get_tag().version_str()

        for name, version in cookbook_info['community'].iteritems():
            if name not in versions:
                versions[name] = version

        for cookbook in repo_list:
            name = cookbook.name
            tag = versions[name]
            self._update_cookbooks(cookbook, tag, versions)

        if self.cleanup:
            util.cleanup()

    def process(self, args):
        processed_args = self.parse_args(args)

        if len(processed_args) > 1:
            logging.error('Error: too many arguments')
        elif len(processed_args) < 1:
            self.print_help()

        repo = processed_args[0]
        self.tag(repo)

    def parse_args(self, args):
        parser = optparse.OptionParser(usage='tina tag <cookbook> [options]')
        parser.add_option('-v', '--verbose',
                          action='store_true',
                          dest='verbose',
                          help='enable verbose logging')
        parser.add_option('-q', '--quiet',
                          action='store_true',
                          dest='quiet',
                          help='disable all logging except errors')
        parser.add_option('-n', '--no-cleanup',
                          action='store_true',
                          dest='no_cleanup',
                          help='leave temporary files after finishing')
        options, args = parser.parse_args(args)

        if options.quiet:
            logging.setLevel(logging.ERROR)
        if options.verbose:
            logging.setLevel(logging.DEBUG)
        if options.no_cleanup:
            self.cleanup = False

        return args

    def print_help(self):
        self.parser.print_help()
