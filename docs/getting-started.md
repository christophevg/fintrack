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
$ export DAY_FIRST=yes                            
% LOG_LEVEL=DEBUG python -m fintrack version
🏦 DEBUG - using a day-first approach
🏦 DEBUG - using /Users/xtof/.fintrack
0.0.1
$ fintrack record -125 "first entry" 7/6
$ ls ~/.fintrack                                  
config.yaml  records.json
% cat ~/.fintrack/records.json
[
  {
    "amount": -125,
    "description": "first entry",
    "timestamp": "2025-06-07T00:00:00",
    "uid": "6ce93412-6f7c-413a-95c5-a046ca5a5cb5"
  }
] 
% python -m fintrack records show       
+---------------------+----------+---------------+--------------------------------------+
| timestamp           |   amount | description   | uid                                  |
+=====================+==========+===============+======================================+
| 2025-06-07T00:00:00 |     -125 | first entry   | 6ce93412-6f7c-413a-95c5-a046ca5a5cb5 |
+---------------------+----------+---------------+--------------------------------------+
```

### Python Module

```python
>>> import json
>>> from fintrack.tracker import Tracker
>>> from fintrack.recorders import RecordEncoder
>>> tracker = Tracker()
>>> tracker.version()
'0.0.1'
>>> tracker.record(-125, "second entry")
>>> print(json.dumps(list(tracker), cls=RecordEncoder, indent=2))
[
  {
    "amount": -125,
    "description": "second entry",
    "timestamp": "2025-06-07T13:01:28.527709",
    "uid": "02e2cb4d-b43e-4e5d-9073-f932180e1e96"
  },
  {
    "amount": -125,
    "description": "first entry",
    "timestamp": "2025-07-06T00:00:00",
    "uid": "82984187-aab1-4a9e-936a-ea5d7037bcf2"
  }
]
>>> tracker.records.show()
'+----------------------------+----------+---------------+--------------------------------------+\n| timestamp                  |   amount | description   | uid                                  |\n+============================+==========+===============+======================================+\n| 2025-06-07T00:00:00        |     -125 | first entry   | 6ce93412-6f7c-413a-95c5-a046ca5a5cb5 |\n+----------------------------+----------+---------------+--------------------------------------+\n| 2025-06-08T14:34:41.600678 |     -125 | second entry  | 7b21c926-cb53-4d3e-a5b8-06e234921b9c |\n+----------------------------+----------+---------------+--------------------------------------+'
```
