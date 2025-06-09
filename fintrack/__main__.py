# ruff: noqa: E402

from fire import Fire

import logging
import os

# load the environment variables for this setup from .env file
from dotenv import load_dotenv
load_dotenv()
load_dotenv(".env")
load_dotenv(".env.local")

# setup logging to stdout

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "INFO"
FORMAT    = "🏦 %(levelname)s %(name)s - %(message)s"
DATEFMT   = "%Y-%m-%d %H:%M:%S %z"

formatter = logging.Formatter(FORMAT, DATEFMT)
logging.basicConfig(level=LOG_LEVEL, format=FORMAT, datefmt=DATEFMT)
logging.getLogger().setLevel(LOG_LEVEL)

# "silence" lower-level modules
for module in [
  "tzlocal"
]:
  module_logger = logging.getLogger(module)
  module_logger.setLevel(logging.WARN)
  if len(module_logger.handlers) > 0:
    module_logger.handlers[0].setFormatter(formatter)



from fintrack.tracker import Tracker

def cli():
  try:
    Fire(Tracker(), name="fintrack")
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  cli()
