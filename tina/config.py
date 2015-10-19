import ConfigParser

class TinaConfig(object):
    git_user = None
    git_url = None
    git_orgs = None
    berks_groups = None

    @classmethod
    def parse_config(cls):
        config_file = '/etc/tina.conf'
        parser = ConfigParser.RawConfigParser()
        parser.readfp(open(config_file))

        cls.git_user = parser.get('git', 'user')
        cls.git_url = parser.get('git', 'url')
        cls.git_orgs = parser.get('git', 'orgs').split(',')

        cls.berks_groups = parser.get('berks', 'exclude').split(',')
