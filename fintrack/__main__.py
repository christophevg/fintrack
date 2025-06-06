from fire import Fire

from fintrack import Tracker

def cli():
  try:
    Fire(Tracker(), name="fintrack")
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  cli()
