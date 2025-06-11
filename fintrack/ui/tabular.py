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
    self.mapping = { key:index for index, key in enumerate(self.sheet.columns) }

  def colorized(self, row):
    if self.colorize:
      for key, rules in self.colorize.items():
        for rule in rules:
          try:
            index = self.mapping[key]
            color = rule(row[index])
            if color:
              row[index] = color + str(row[index]) + Style.RESET_ALL
          except KeyError:
            pass
    return row
    
  def __str__(self):
    return tabulate( [
      self.colorized(row) for row in self.sheet.rows
    ], self.sheet.columns, tablefmt="grid" )

def positive_green(value):
  try:
    if value > 0:
      return Fore.GREEN
  except TypeError:
    pass

def negative_red(value):
  try:
    if value < 0:
      return Fore.RED
  except TypeError:
    pass
