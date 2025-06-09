import os

import re

from datetime import datetime
import uuid

import humanize

import logging
logger = logging.getLogger(__name__)

DATE_ORDER = os.environ.get("DATE_ORDER", "DMY")
if DATE_ORDER:
  logging.debug(f"using a date order {DATE_ORDER}")

DATE_LANG = os.environ.get("DATE_LANG", None)
if DATE_LANG:
  humanize.i18n.activate(DATE_LANG)
  logging.debug(f"using date language {DATE_LANG}")

DECIMAL_POINT = os.environ.get("DECIMAL_POINT", ",")

def now():
  return datetime.now() # wrapped to be able to monkeypatch it in tests

def uid():
  return str(uuid.uuid4()) # wrapped to be able to monkeypatch it in tests

def parse_amount(amount):
  # remove everything that shouldn't be in there
  if DECIMAL_POINT == ".":
    amount = re.sub("[^\d.-]","", amount)
  else:
    amount = re.sub(DECIMAL_POINT, ".", re.sub(f"[^\d{DECIMAL_POINT}-]","", amount))
  return float(amount)
