# ruff: noqa: E402

from fire import Fire

import logging
import os

# setup logging to stdout

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
FORMAT    = "🏦 %(levelname)s - %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

formatter = logging.Formatter(FORMAT, DATEFMT)
logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
logging.getLogger().setLevel(LOG_LEVEL)

from fintrack.tracker import Tracker

def cli():
  try:
    Fire(Tracker(), name="fintrack")
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  cli()
