#!/usr/bin/env python3
# Clue quiz
# Copyright (C) 2018-2022  Luca Schmid

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

from argparse import ArgumentParser
from paho.mqtt.client import Client
from json import loads
from random import choice
from re import match
from sys import exit, stderr
from signal import SIGINT, pause, signal
import requests

playlists = {
    'select': [],
    'respond': [],
    'correct': [],
    'wrong': []
}

consumed = {
    'select': [],
    'respond': [],
    'correct': [],
    'wrong': []
}

def on_connect(client, userdata, flags, rc):
    client.subscribe(userdata['topic'])

def on_message(client, userdata, msg):
    name = loads(msg.payload)['name']
    if len(playlists[name]) == 0 and len(consumed[name]) > 0:
        playlists[name] = consumed[name]
        consumed[name] = []

    if len(playlists[name]) > 0:
        s = choice(playlists[name])
        group, sound = match(r'(.+)/(.+)\.[^.]+', s).groups()

        try:
            r = requests.post(f'https://{userdata["soundboard"]}/api/play', json={'group': group, 'sound': sound})
            r.raise_for_status()
        except requests.RequestException as e:
            print(e, file=stderr, flush=True)
            return

        playlists[name].remove(s)
        consumed[name].append(s)

def signal_handler(sig, frame):
    client.loop_stop()
    client.disconnect()
    exit(0)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--topic')
    parser.add_argument('host')
    parser.add_argument('playlist')
    parser.add_argument('soundboard')
    args = parser.parse_args()

    with open(args.playlist, 'r') as f:
        playlists = loads(f.read())

    client = Client()
    client.user_data_set({'soundboard': args.soundboard, 'topic': args.topic or 'cluequiz'})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(args.host)
    client.loop_start()

    signal(SIGINT, signal_handler)
    pause()
