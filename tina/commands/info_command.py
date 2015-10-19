class InfoCommand(object):
    def __init__(self):
        pass

    @staticmethod
    def get_verb_name():
        return 'info'

    def process(self, args):
        print 'nothing to see here...'

    def print_help(self):
        print 'info command help coming soon!'
