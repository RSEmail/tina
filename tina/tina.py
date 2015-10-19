import difflib
import logging
import sys

import commands
import config
import _version

def get_verb_map():
    verb_map = {}
    for command_class in commands.commands:
        verb_map[command_class.get_verb_name()] = command_class

    return verb_map

def print_help():
    print 'usage: tina [--version] [--help] <command> [<args>]'
    print
    print 'The available tina commands are:'
    for verb in sorted(get_verb_map().keys()):
        print '\t{0}'.format(verb)
    print
    print 'See "tina help <command>" to read about a specific command.'

def print_command_help(verb):
    get_class_from_verb(verb).print_help()

def print_version():
    print 'tina version {0}'.format(_version.__version__)

def handle_invalid_verb(verb):
    print '"{0}" is not a valid tina command. See "tina --help".'.format(verb)

    close_verbs = difflib.get_close_matches(verb, get_verb_map().keys())
    if close_verbs:
        print
        print 'Did you mean this?'
        for v in close_verbs:
            print '\t{0}'.format(v)
    sys.exit(1)

def get_class_from_verb(verb):
    try:
        return get_verb_map()[verb]()
    except KeyError:
        raise ValueError('Invalid verb: {0}'.format(verb))

def initialize():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format='%(message)s')
    config.TinaConfig.parse_config()

def process_args():
    if len(sys.argv) < 2:
        print_help()
    else:
        first = sys.argv[1]
        rest = sys.argv[2:]

        if first == '--help':
            print_help()
        elif first == '--version':
            print_version()
        elif first == 'help':
            if len(rest) < 1:
                print_help()
            else:
                print_command_help(rest[0])
        else:
            try:
                module = get_class_from_verb(first)
            except ValueError:
                handle_invalid_verb(first)
            module.process(rest)

def main():
    initialize()
    process_args()

if __name__ == "__main__":
    main()
