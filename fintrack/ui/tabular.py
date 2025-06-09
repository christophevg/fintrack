from tabulate import tabulate
from colorama import Fore, Style, init

from fintrack.util import get_columns, asrow

import logging
logger = logging.getLogger(__name__)

# reset coloring in between prints
init(autoreset=True)

class Tabular:
  """
  given a list of objects, visualize it as a table, adding color according to
  provided rules { key, [fun(value)->color)] }
  """
  def __init__(self, objects, colorize=None, balanced=None):
    self.objects  = objects
    self.colorize = colorize if colorize else {}
    self.balanced = balanced

  @property
  def columns(self):
    if len(self.objects) > 0:
      columns = get_columns(self.objects[0])
      if self.balanced:
        return self.balanced(columns, headers=True)
      return columns
    return []

  @property
  def rows(self):
    r = []
    for obj in self.objects:
      row = asrow(obj)
      if row:
        r.append(row)
    if self.balanced:
      return self.balanced(r)
    return r

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
      self.colorized(row) for row in self.rows
    ], self.columns, tablefmt="grid" )

def positive_green(value):
  if value > 0:
    return Fore.GREEN

def negative_red(value):
  if value < 0:
    return Fore.RED
