import os
import re
import shutil
import sys
from cookbook_repo import *
from gitlib import *
from parse_berk import *
from community_cookbooks import *
from tag import Tag

def tag_compare(x, y):
    x_nums = x.split(".")
    y_nums = y.split(".")
    for (x,y) in zip(x_nums,y_nums):
        if x != y:
            return int(x) - int(y)
    return 0

def cleanup():
    if os.path.exists(".tina"):
        shutil.rmtree(".tina")

def recurse_discover_cookbooks(available_cookbooks, taggable_cookbooks, root_repo):
    for depends in root_repo.metadata.depends:
        found = False
        for cookbook in available_cookbooks:
            if cookbook["name"] == depends:
                found = True
                if cookbook["taggable"]:
                    if not cookbook["name"] in taggable_cookbooks.keys():
                        print("Discovered cookbook to tag %s" % cookbook["name"])
                        taggable_cookbooks[cookbook["name"]] = CookbookRepo(cookbook["rw_url"])
                        recurse_discover_cookbooks(available_cookbooks, taggable_cookbooks, taggable_cookbooks[cookbook["name"]])

    if not found:
        print("%s depends on %s but it is not available" % (root_repo.metadata.cookbook_name, depends))
        exit()

def get_name_from_url(repo_url):
    match = re.match(".*/(.+?)\.git.*", repo_url)
    if not match:
        raise Exception("Error: git URL is malformed: '%s'" % repo_url)
    return match.group(1)

def checkout_and_parse(path):
    cleanup()

    available_cookbooks = cookbooks_from_berks()
    root_repo = CookbookRepo(get_local_repo_url())
    taggable_cookbooks = {}
    taggable_cookbooks[root_repo.metadata.cookbook_name] = root_repo
    recurse_discover_cookbooks(available_cookbooks, taggable_cookbooks, root_repo) 

    versions = {}
    for cookbook in available_cookbooks:
        versions[cookbook["name"]] = cookbook["tag"]

    for cookbook_name, repo in taggable_cookbooks.items():
        versions[cookbook_name] = repo.new_tag

    for name, version in versions.items():
        print("%s is version %s" %(name, version.version_str()))


def print_summary(repos, cookbooks):
    print "REPOSITORY SUMMARY:"
    for _,repo in repos.items():
        if repo.changed:
            print "%s: %s => %s" % (repo.name, repo.old_tag, repo.new_tag)
        else:
            print "%s: unchanged" % repo.name

    print
    print "COMMUNITY COOKBOOK SUMMARY:"
    for name,version in cookbooks.items():
        print "%s will be pinned at %s" % (name, version)

def generate_tinafile(repos, cookbooks):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# These are taggable cookbook repos. Repos prepended\n"
        "# with a + will have versions pinned, be tagged, and\n"
        "# will be pushed to their upstream remotes.\n")

    for _,repo in repos.items():
        format_str = "+%s: %s\n" if repo.changed else "%s: %s\n"
        tinafile.write(format_str % (repo.metadata.cookbook_name, repo.new_tag))

    tinafile.write("# Pinned community cookbooks:\n")
    for name,version in cookbooks.items():
        tinafile.write("%s: %s\n" % (name, version))

    tinafile.close()

def commit_and_push():
    repo_list, versions = parse_tinafile()

    for name in repo_list:
        cookbook_repo = CookbookRepo(name)
        cookbook_repo.changed = True
        cookbook_repo.new_tag = versions[name]
        cookbook_repo.resolve_deps(versions)
        cookbook_repo.commit()

def parse_tinafile():
    tinafile = open(".tina/Tinafile", "r")
    lines = tinafile.readlines()

    repo_list = [ ]
    versions = { }
    cookbook_regex = re.compile("^(\+?)([\w\-\.]+)\s*:\s*([\w\-\.]+)\s*$")
    for line in lines:
        if line[0] == "#":
            continue

        line = line.rstrip()
        match = cookbook_regex.match(line)
        if not match:
            raise Exception("Invalid line in Tinafile: '%s'" % line)

        versions[match.group(2)] = Tag(match.group(3))
        if match.group(1) == "+":
            repo_list.append(match.group(2))

    tinafile.close()
    return repo_list, versions
