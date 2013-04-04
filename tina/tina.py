import argparse
import os
import sys
from tina_util import *

def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--commit", action="store_true",
        help="Commit changes to remotes (default: dry-run only)")
    parser.add_argument("-i", "--interactive", action="store_true",
        help="Run in interactive mode")
    parser.add_argument("-n", "--no-cleanup", action="store_true",
            help="Don't remove temporary files after committing")
    return parser.parse_args()

def main():
    args = handle_args()

    if not args.commit or not os.path.exists(".tina"):
        checkout_and_parse(".", args.interactive)

    if args.commit:
        commit_and_push()
        if not args.no_cleanup:
            cleanup()

if __name__ == "__main__":
    main()
