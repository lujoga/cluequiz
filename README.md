# Clue quiz

**Note**: Clue quiz seems to break with PyGame 2. If you use PyGame 1.9.6, you should be fine. For now, the dependency will be pinned to version 1.9.6. If your system does not have the required version, you can run clue quiz with Docker (assuming you use X11):

```
xauth nlist "$DISPLAY" | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge -
sudo docker-compose up
```

**Note**: If you're on an M1 Mac, you may encounter an error saying the `pygame.mixer` module could not be found. In this case, [you will have to build PyGame from source](https://stackoverflow.com/a/68877135), though the above probably still applies, i.e. you need PyGame 1.9.6 and SDL 1.2.

## Installation

First, clone the repository and cd into the newly created directory:

```
git clone https://github.com/lujoga/cluequiz
cd cluequiz
```

It is recommended to create a Python virtual environment to install clue quiz in:

```
virtualenv env
source env/bin/activate
```

Then install the module by executing the following command:

```
pip install .
```

If there is an error installing `pygame`, you may need to install the SDL libraries beforehand.

## Setup

Clue quiz requires a config file `config.yml` and one or more clue sets specified in the config. The config file should look something like this:

```YAML
clue-sets:
  - clue-set01.yml
  - clue-set02.yml
  - ...
```

Every clue set has six categories with five clue-question pairs each:

```YAML
Category 1:
  - clue: Clue 1
    question: Question 1
  - clue: Clue 2
    question: Question 2
  - clue: Clue 3
    question: Question 3
  - clue: Clue 4
    question: Question 4
  - clue: Clue 5
    question: Question 5
Category 2:
  - ...
```

Sounds can be used as clues by supplying a `sound` key instead of `clue`:

```YAML
- ...
- sound: sound.ogg
  question: What is ...?
```

To use an image as a clue replace the `clue` key with an `image` key. An optional `bg` key may also be specified to fill the background with the given color:

```YAML
- ...
- image: image.jpg
  bg: [255, 255, 255]
  question: Question?
- ...
```

If you want to display code as a clue, you can have it syntax-highlighted by specifying a `lang` key:

```YAML
- ...
- clue: |
        a = 3
        b = 4
        c = (a**2 + b**2)**0.5
        assert c == 5.0
  lang: python
  question: What is a Pythagorean triple?
- ...
```

### Optional configuration keys

* Setting the `ignore-responded` key to `true` lets players respond infinitely often, but also subtracts points from their scores every time they answer wrongly.
* Setting the `viewer` key to `true` activates viewer mode, i.e. selecting a clue displays the corresponding question immediately. This is handy when hosting a game created by others.
* Set the `music` key to either a single file or a list of files containing music you want to play to help players think.

### Serial configuration

If clue quiz is able to establish a connection to /dev/ttyUSB0, the serial port will be read instead of polling keys '1', '2', '3' and '4'. To connect to some other port or use a different baud rate, `serial.port` and `serial.baud` can be set in the config:

```YAML
serial:
  port: /dev/ttyUSB0
  baud: 9600
```

### MQTT configuration

Clue quiz publishes JSON objects via MQTT if the `mqtt.host` key is specified. You may also set `mqtt.port` and `mqtt.topic` to use a port or topic deviating from the default (`1883` and `cluequiz`, respectively).

```YAML
mqtt:
  host: mqtt.example.com
  port: 1883
  topic: cluequiz
```

The published JSON objects have `name`, `player` and `value` attributes. `name` is one of `select`, `respond`, `correct` and `wrong`. `value` is the amount of points associated with the selected clue.

* For `"name": "select"`, `player` is the id (0 to 3) of the selecting player.
* For `"name": "respond"`, `"name": "correct"` and `"name": "wrong"`, `player` is the id (0 to 3) of the responding player.

## Usage

To start clue quiz, enter the virtual environment if you have not already and run `cluequiz`:

```
source env/bin/activate
cluequiz
```

In any screen, previous actions that changed the game state can be undone by pressing 'U'.

### Choosing

In the clue selection screen, one can choose a clue by clicking the respective field. To set a player's name, press '1' (red), '2' (green), '3' (blue) or '4' (yellow) on the keyboard (serial input won't work), type their name and hit the return key.

### Display clue

Once the clue is displayed, the players can ring-in by pressing '1', '2', '3' or '4' on the keyboard or send '1', '2', '3' or '4' via the serial connection. Pressing 'Backspace' jumps back to the clue selection screen. 'Delete' removes the clue for this game. If the clue is a sound, it can be played again by hitting 'Space'. Music is started (and stopped) with the 't' key, if configured.

### Responding

Press 'j' to signal a correct or 'n' for a wrong response. If the answer is correct, the corresponding question is displayed. If it is wrong, the other players will be given the chance to ring-in. If no player has responded correctly, the clue is removed.

### Display question and scoreboard

Any key goes back to either the selection screen or the scoreboard, depending on the game's state.
