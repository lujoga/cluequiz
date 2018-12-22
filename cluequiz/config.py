from os import environ
from yaml import load


class Config():
    """Loads configuration from environment variables."""
    UNSET = object()

    def __init__(self):
        self.config_file = environ.get('CONFIG_FILE', 'config.yml')
        with open(self.config_file) as f:
            self.config = load(f)

        if 'debug' not in self.config:
            self.config['debug'] = False

        if 'DEBUG' in environ:
            self.config['debug'] = environ.get('DEBUG', 'False') in ['True', 'true', 'yes', 'y']

        print(self.config)

    def __call__(self, key, default=UNSET):
        """Query for a configuration variable."""
        if key == 'debug':
            return self.debug
        try:
            return self._resolve(key, self.config)
        except KeyError as _:
            if default is self.UNSET:
                raise SystemExit('Required config key "%s" is missing' % key)
            return default

    def _resolve(self, key, search_dict):
        """Get items and subitems from dict using 'key.subkey'."""
        if '.' in key:
            key, sub_key = key.split('.', 1)
            return self._resolve(sub_key, search_dict[key])
        return search_dict[key]

    @property
    def debug(self):
        return self.config.get('debug', False)


config = Config()
