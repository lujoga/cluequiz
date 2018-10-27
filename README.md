# Clue quiz

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

### Serial configuration

If clue quiz is able to establish a connection to /dev/ttyUSB0, the serial port will be read instead of polling keys '1', '2', '3' and '4'. To connect to some other port or use a different baud rate, `serial.port` and `serial.baud` can be set in the config:

```YAML
serial:
  port: /dev/ttyUSB0
  baud: 9600
```

## Usage

To start clue quiz, enter the virtual environment if you have not already and run the module 'cluequiz':

```
source env/bin/activate
python -m cluequiz
```

### Choosing

In the clue selection screen, one can choose a clue by clicking the respective field.

### Display clue

Once the clue is displayed, the players can ring-in by pressing '1', '2', '3' or '4' on the keyboard or send '1', '2', '3' or '4' via the serial connection. Pressing 'Backspace' jumps back to the clue selection screen. 'Delete' removes the clue for this game.

### Responding

Press 'j' to signal a correct or 'n' for a wrong response. If the answer is correct, the corresponding question is displayed. If it is wrong, the other players will be given the chance to ring-in. If no player has responded correctly, the clue is removed.

### Display question and scoreboard

Any key goes back to either the selection screen or the scoreboard, depending on the game's state.
