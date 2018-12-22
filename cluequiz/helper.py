from collections import namedtuple
from logging import getLogger


logger = getLogger(__name__)
GameStateHistory = namedtuple('GameStateHistory', ['state', 'scores', 'choosing', 'responded'])
