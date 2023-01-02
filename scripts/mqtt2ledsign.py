#!/usr/bin/env python3
# Clue quiz
# Copyright (C) 2018-2023  Luca Schmid

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
from json import loads
from paho.mqtt.client import Client
from random import choice
from sys import exit
from time import sleep, time

fx = {}
idle = None

def on_connect(client, userdata, flags, rc):
    client.subscribe(userdata['topic'])

def on_message(client, userdata, msg):
    event = loads(msg.payload)
    name = event['name']
    player = event['player']
    if name not in fx or player > len(fx[name]):
        return

    cmd_topic = userdata['device'] + '/api'
    for cmd in choice(fx[name][player]):
        if cmd.startswith('SLEEP'):
            sleep(int(cmd.split('=')[1]))
        else:
            client.publish(cmd_topic, cmd)

    if idle:
        for cmd in choice(idle):
            client.publish(cmd_topic, cmd)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--topic')
    parser.add_argument('-d', '--device')
    parser.add_argument('host')
    parser.add_argument('fx')
    args = parser.parse_args()

    with open(args.fx, 'r') as f:
        fx = loads(f.read())
    if 'idle' in fx:
        idle = fx['idle']

    client = Client()
    client.user_data_set({'topic': args.topic or 'cluequiz', 'device': args.device or 'ledsign'})
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect_async(args.host)
    client.loop_start()

    signal(SIGINT, signal_handler)
    pause()
