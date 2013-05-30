import optparse
import os
import sys
from tina_util import *
from _version import __version__

def handle_args():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--commit", action="store_true",
        help="Commit changes to remotes (default: dry-run only)")
    parser.add_option("-i", "--interactive", action="store_true",
        help="Run in interactive mode")
    parser.add_option("-n", "--no-cleanup", action="store_true",
            help="Don't remove temporary files after committing")
    parser.add_option("-v", "--version", action="store_true",
            help="Print version information")
    options, args = parser.parse_args()
    return options

def main():
    args = handle_args()

    if args.version:
        print "tina %s" % __version__
        return

    if not args.commit or not os.path.exists(".tina"):
        checkout_and_parse(".", args.interactive)

    if args.commit:
        commit_and_push()
        if not args.no_cleanup:
            cleanup()
    else:
        print "To commit these changes, re-run with --commit"

if __name__ == "__main__":
    main()
