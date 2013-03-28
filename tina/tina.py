import os
import sys
from cookbook_repo import *
from tina_util import *

def main():
    commit = False
    for arg in sys.argv[1:]:
        if arg == "--commit":
            commit = True
        else:
            print "option %s not recognized" % arg
            sys.exit(1)

    if not commit: # This is a dry-run.
        checkout_and_parse(".")
    #else:
    #    for repo_name in os.listdir(".tina"):
    #        commit_and_push(git.Repo(".tina/%s" % repo_name), repo_name)

if __name__ == "__main__":
    main()
