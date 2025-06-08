# Getting Started

## Install

FinTrack is hosted on PyPI...

```console
$ pip install fintrack
```

## Basic Usage

FinTrack kan be used as a console/command line tool or as a Python module:

### Console

```console
% export DATE_ORDER=DMY
% export DATE_LANG=nl_NL
% LOG_LEVEL=DEBUG fintrack version
🏦 DEBUG - using a date order DMY
🏦 DEBUG - using date language nl_NL
🏦 DEBUG - using /Users/xtof/.fintrack
0.0.1

% date
Sun Jun  8 16:21:38 CEST 2025

% fintrack record 125 "starting balance" today
% fintrack records show                       
+-------------+----------+-----------+------------------+--------------------------------------+
| timestamp   |   amount |   balance | description      | uid                                  |
+=============+==========+===========+==================+======================================+
| vandaag     |      125 |       125 | starting balance | 88c9aec8-6f5c-41b1-a41e-099c6cde4928 |
+-------------+----------+-----------+------------------+--------------------------------------+

% cat ~/.fintrack/records.json
[
  {
    "amount": 125,
    "description": "starting balance",
    "timestamp": "2025-06-08T16:22:22.352984",
    "uid": "88c9aec8-6f5c-41b1-a41e-099c6cde4928"
  }
] 
```

### Python Module

```python
>>> import json
>>> from fintrack.tracker import Tracker
>>> from fintrack.recorders import RecordEncoder
>>> tracker = Tracker()
>>> tracker.version()
'0.0.1'
>>> tracker.record(-200, "first payment")
>>> print(json.dumps(list(tracker), cls=RecordEncoder, indent=2))
[
  {
    "amount": 125,
    "description": "starting balance",
    "timestamp": "2025-06-08T16:22:22.352984",
    "uid": "88c9aec8-6f5c-41b1-a41e-099c6cde4928"
  },
  {
    "amount": -200,
    "description": "first payment",
    "timestamp": "2025-06-08T16:24:29.658952",
    "uid": "d6e2ab00-c99d-429f-9fe7-3d8b4cf9ef93"
  }
]
>>> tracker.records.show()
'+-------------+----------+-----------+------------------+--------------------------------------+\n| timestamp   |   amount |   balance | description      | uid                                  |\n+=============+==========+===========+==================+======================================+\n| vandaag     |      125 |       125 | starting balance | 88c9aec8-6f5c-41b1-a41e-099c6cde4928 |\n+-------------+----------+-----------+------------------+--------------------------------------+\n| vandaag     |     -200 |       \x1b[31m-75\x1b[0m | first payment    | d6e2ab00-c99d-429f-9fe7-3d8b4cf9ef93 |\n+-------------+----------+-----------+------------------+--------------------------------------+'
```
