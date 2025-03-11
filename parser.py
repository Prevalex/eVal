import argparse

class TheArgParserException(Exception):
    """
    https://ru.stackoverflow.com/questions/1524220
    """
    def __init__(self, message):
        super().__init__(message)

class NoExitArgumentParser(argparse.ArgumentParser):
    """
    https://ru.stackoverflow.com/questions/1524220
    """
    def error(self, message):
        raise TheArgParserException(message)