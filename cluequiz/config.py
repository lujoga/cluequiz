import os


class Config():
    """Loads configuration from environment variables."""
    debug = False

    def __init__(self):
        if os.environ.get('DEBUG', 'False') in ['True', 'true', 'yes', 'y']:
            self.debug = True


config = Config()
