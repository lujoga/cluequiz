# Clue quiz
# Copyright (C) 2018-2021  Luca Schmid

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from os import environ
from yaml import load


class Config():
    """Loads configuration from environment variables."""
    UNSET = object()

    def __init__(self):
        self.config_file = environ.get('CONFIG_FILE', 'config.yml')
        with open(self.config_file) as f:
            self.config = load(f)

        if 'DEBUG' in environ:
            self.config['debug'] = environ.get('DEBUG', 'False') in ['True', 'true', 'yes', 'y']
        if 'VIEWER' in environ:
            self.config['viewer'] = environ.get('VIEWER', 'False') in ['True', 'true', 'yes', 'y']

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

    @property
    def viewer(self):
        return self.config.get('viewer', False)


config = Config()
