import os
import shutil
import sys
from cookbook_repo import *
from gitlib import *
from parse_berk import *
from community_cookbooks import *

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
    print "COOKBOOK SUMMARY:"
    for name,version in cookbooks.items():
        print "%s will be pinned at %s" % (name, version)

def generate_tinafile(repos, cookbooks):
    tinafile = open(".tina/Tinafile", "w")

    tinafile.write("# Taggable git repos:\n")
    for _,repo in repos.items():
        if repo.changed:
            tinafile.write("%s: %s\n" % (repo.name, repo.new_tag))

    tinafile.write("# Pinned community cookbooks:\n")
    for name,version in cookbooks.items():
        tinafile.write("+%s: %s\n" % (name, version))

    tinafile.close()
