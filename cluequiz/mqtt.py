# Clue quiz
# Copyright (C) 2019  Luca Schmid

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

from cluequiz.config import config
from paho.mqtt.publish import single
from json import dumps

def publish_event(name, player, value):
    host = config('mqtt.host', None)
    if host:
        port = config('mqtt.port', 1883)
        topic = config('mqtt.topic', 'cluequiz')
        single(topic, dumps({ 'name': name, 'player': player, 'value': value }), hostname=host, port=port)
