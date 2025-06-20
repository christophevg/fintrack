import os

import re

from dataclasses import is_dataclass, asdict, fields
from collections.abc import Iterable

import json

from dateparser import parse
from datetime import datetime
import uuid
import numbers
from decimal import Decimal

import humanize

import logging
logger = logging.getLogger(__name__)

DATE_ORDER = os.environ.get("DATE_ORDER", "DMY")
if DATE_ORDER:
  logger.debug(f"using a date order {DATE_ORDER}")

DATE_LANG = os.environ.get("DATE_LANG", None)
if DATE_LANG:
  humanize.i18n.activate(DATE_LANG)
  logger.debug(f"using date language {DATE_LANG}")

DECIMAL_POINT = os.environ.get("DECIMAL_POINT", ",")

def now():
  return datetime.now() # wrapped to be able to monkeypatch it in tests

def uid():
  return str(uuid.uuid4()) # wrapped to be able to monkeypatch it in tests

def parse_amount(amount):
  if not isinstance(amount, numbers.Number):
    # remove everything that shouldn't be in there
    if DECIMAL_POINT == ".":
      amount = re.sub(r'[^\d.-]',"", amount)
    else:
      amount = re.sub(DECIMAL_POINT, ".", re.sub(r'[^\d'+f"{DECIMAL_POINT}-]","", amount))
  return Decimal(amount)

def parse_datetime(dt_str):
  return parse(dt_str, settings={"DATE_ORDER": DATE_ORDER})

class ClassEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Iterable):
      return list(obj)
    if is_dataclass(obj):
      return asdict(obj)
    if isinstance(obj, datetime):
      return obj.isoformat()
    if isinstance(obj, Decimal):
      return str(obj)
    return super().default(obj)

def ClassDecoder(cls):
  class WrappedClassDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
      self.cls = cls
      self.types = { field.name : field.type for field in fields(self.cls) }
      super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, dct):
      for key, value in dct.items():
        if self.types.get(key, None) is datetime:
          dct[key] = datetime.fromisoformat(value)
      return self.cls(**dct)
  return WrappedClassDecoder

def get_columns(obj):
  try:
    # should be a Record or a PlannedRecord, which exposes its columns
    return list(obj.columns)
  except AttributeError:
    try:
      # maybe it's a plain dataclass?
      return [ fld.name for fld in fields(obj) ]
    except TypeError:
      try:
        # maybe it's a plain dict?
        return list(obj.keys())
      except AttributeError:
        # no clue 🤷‍♂️
        logger.error(f"can't extract columns from {obj}")
        pass
  return []

def humanized(value):
  if isinstance(value, datetime):
    return humanize.naturalday(value)
  if isinstance(value, Decimal):
    return float(value)
  return value

def asrow(obj):
  if isinstance(obj, dict):
    d = obj.copy()
  else:
    # should be a dataclass then
    try:
      d = asdict(obj)
    except TypeError:
      logger.warning(f"don't know how to make a dict of {obj}")
      d = None
  if d:
    return [ humanized(d[key]) for key in get_columns(obj) ]
  return None

def all_subclasses(cls):
  return set(cls.__subclasses__()).union(
    [ s for c in cls.__subclasses__() for s in all_subclasses(c) ]
  )
