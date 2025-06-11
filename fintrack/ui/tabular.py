from tabulate import tabulate
from colorama import Fore, Style, init

import logging
logger = logging.getLogger(__name__)

# reset coloring in between prints
init(autoreset=True)

class Tabular:
  """
  given a sheet, visualize it as a table, adding color according to
  provided rules { key, [fun(value)->color)] }
  """
  def __init__(self, sheet, colorize=None):
    self.sheet    = sheet
    self.colorize = colorize if colorize else {}

  def colorized(self, row):
    if not self.colorize:
      return row
    for key, rules in self.colorize.items():
      for rule in rules:
        try:
          color = rule(row[key])
          if color:
            row[key] = color + row[key] + Style.RESET_ALL
        except KeyError:
          pass
    
  def __str__(self):
    return tabulate( [
      self.colorized(row) for row in self.sheet.rows
    ], self.sheet.columns, tablefmt="grid" )

def positive_green(value):
  if value > 0:
    return Fore.GREEN

def negative_red(value):
  if value < 0:
    return Fore.RED
