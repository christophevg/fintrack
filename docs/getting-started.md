# Getting Started

FinTrack allows you to record financial transactions (income & expenses), both actuals as planned. It has the notion of sheets to group related records.

## Install

FinTrack is hosted on PyPI...

```console
$ pip install fintrack
```

## Basic Usage

FinTrack kan be used as a console/command line tool or as a Python module

### Console

```console
% export DATE_ORDER=DMY
% export DATE_LANG=nl_NL
% LOG_LEVEL=DEBUG fintrack version
🏦 DEBUG fintrack.util - using a date order DMY
🏦 DEBUG fintrack.util - using date language nl_NL
🏦 DEBUG fintrack.tracker - using /Users/xtof/.fintrack
🏦 WARNING fintrack.tracker - /Users/xtof/.fintrack doesn't contain config.yaml
🏦 INFO fintrack.tracker - activated sheet 'records'
0.0.1

% date
Tue Jun 10 12:05:39 CEST 2025

% fintrack add 125 "starting balance" today
🏦 WARNING fintrack.tracker - /Users/xtof/.fintrack doesn't contain config.yaml
🏦 INFO fintrack.tracker - activated sheet 'records'
🏦 INFO fintrack.tracker - added record for 125 vandaag starting balance

% % fintrack table
🏦 INFO fintrack.tracker - activated sheet 'records'
+-------------+----------+------------------+--------------------------------------+
| timestamp   |   amount | description      | uid                                  |
+=============+==========+==================+======================================+
| vandaag     |      125 | starting balance | 9c7e6ce9-1c0c-47fb-878e-96253438b106 |
+-------------+----------+------------------+--------------------------------------+

% cat ~/.fintrack/records.json
[
  {
    "amount": "125",
    "description": "starting balance",
    "timestamp": "2025-06-10T12:05:55.851083",
    "uid": "9c7e6ce9-1c0c-47fb-878e-96253438b106"
  }
] 
```

### Python Module

```python
>>> import json
>>> from fintrack.tracker import Tracker
>>> from fintrack.util import ClassEncoder
>>> tracker = Tracker()
>>> tracker.version()
'0.0.1'
>>> tracker.add(-200, "first payment")
>>> print(json.dumps(list(tracker), cls=ClassEncoder, indent=2))
[
  {
    "amount": "125",
    "description": "starting balance",
    "timestamp": "2025-06-10T12:05:55.851083",
    "uid": "9c7e6ce9-1c0c-47fb-878e-96253438b106"
  },
  {
    "amount": "-200",
    "description": "first payment",
    "timestamp": "2025-06-10T12:07:52.409001",
    "uid": "0357955f-9f2c-493b-9323-fbfea0a25938"
  }
]
>>> print(tracker.table)
+-------------+----------+------------------+--------------------------------------+
| timestamp   |   amount | description      | uid                                  |
+=============+==========+==================+======================================+
| vandaag     |      125 | starting balance | 9c7e6ce9-1c0c-47fb-878e-96253438b106 |
+-------------+----------+------------------+--------------------------------------+
| vandaag     |     -200 | first payment    | 0357955f-9f2c-493b-9323-fbfea0a25938 |
+-------------+----------+------------------+--------------------------------------+
```

## Planning

FinTrack also allows you to make plans using PlannedRecords:

```console
% fintrack sheet plans add 5 "daily saving" "every other day" "saving on {date}"
🏦 WARNING fintrack.tracker - could not find sheet plans.json
🏦 INFO fintrack.tracker - activated sheet 'records'
🏦 INFO fintrack.tracker - activated sheet 'plans'
🏦 INFO fintrack.tracker - added plan for 5 every other day daily saving
% fintrack sheet plans add -125 "groceries" "every friday" "groceries on {date}"
🏦 INFO fintrack.tracker - activated sheet 'records'
🏦 INFO fintrack.tracker - activated sheet 'plans'
🏦 INFO fintrack.tracker - added plan for -125 every friday groceries
% fintrack sheet plans table
🏦 INFO fintrack.tracker - activated sheet 'records'
🏦 INFO fintrack.tracker - activated sheet 'plans'
+-----------------+----------+---------------+---------------------+--------------------------------------+
| schedule        |   amount | description   | uids                | uid                                  |
+=================+==========+===============+=====================+======================================+
| every other day |        5 | daily saving  | saving on {date}    | 1a7c218f-d2a6-495b-874e-0d6ef6db13ea |
+-----------------+----------+---------------+---------------------+--------------------------------------+
| every friday    |     -125 | groceries     | groceries on {date} | f70403d8-94d0-4056-ba34-cb44e12feede |
+-----------------+----------+---------------+---------------------+--------------------------------------+
% fintrack future "next month" table
🏦 INFO fintrack.tracker - activated sheet 'records'
+-------------+----------+---------------+---------------------+
| timestamp   |   amount | description   | uid                 |
+=============+==========+===============+=====================+
| Jun 12      |        5 | daily saving  | saving on Jun 12    |
+-------------+----------+---------------+---------------------+
| Jun 13      |     -125 | groceries     | groceries on Jun 13 |
+-------------+----------+---------------+---------------------+
| Jun 14      |        5 | daily saving  | saving on Jun 14    |
+-------------+----------+---------------+---------------------+
| Jun 16      |        5 | daily saving  | saving on Jun 16    |
+-------------+----------+---------------+---------------------+
| Jun 18      |        5 | daily saving  | saving on Jun 18    |
+-------------+----------+---------------+---------------------+
| Jun 20      |        5 | daily saving  | saving on Jun 20    |
+-------------+----------+---------------+---------------------+
| Jun 20      |     -125 | groceries     | groceries on Jun 20 |
+-------------+----------+---------------+---------------------+
| Jun 22      |        5 | daily saving  | saving on Jun 22    |
+-------------+----------+---------------+---------------------+
| Jun 24      |        5 | daily saving  | saving on Jun 24    |
+-------------+----------+---------------+---------------------+
| Jun 26      |        5 | daily saving  | saving on Jun 26    |
+-------------+----------+---------------+---------------------+
| Jun 27      |     -125 | groceries     | groceries on Jun 27 |
+-------------+----------+---------------+---------------------+
| Jun 28      |        5 | daily saving  | saving on Jun 28    |
+-------------+----------+---------------+---------------------+
| Jun 30      |        5 | daily saving  | saving on Jun 30    |
+-------------+----------+---------------+---------------------+
| Jul 02      |        5 | daily saving  | saving on Jul 02    |
+-------------+----------+---------------+---------------------+
| Jul 04      |        5 | daily saving  | saving on Jul 04    |
+-------------+----------+---------------+---------------------+
| Jul 04      |     -125 | groceries     | groceries on Jul 04 |
+-------------+----------+---------------+---------------------+
| Jul 06      |        5 | daily saving  | saving on Jul 06    |
+-------------+----------+---------------+---------------------+
| Jul 08      |        5 | daily saving  | saving on Jul 08    |
+-------------+----------+---------------+---------------------+
| Jul 10      |        5 | daily saving  | saving on Jul 10    |
+-------------+----------+---------------+---------------------+
```

Records can be "balanced" and the "overview" shows recent and future expected transactions:

```console
% fintrack overview balanced table
🏦 INFO fintrack.tracker - activated sheet 'records'
+-------------+----------+-----------+------------------+--------------------------------------+
| timestamp   |   amount |   balance | description      | uid                                  |
+=============+==========+===========+==================+======================================+
| vandaag     |      125 |       125 | starting balance | 9c7e6ce9-1c0c-47fb-878e-96253438b106 |
+-------------+----------+-----------+------------------+--------------------------------------+
| vandaag     |     -200 |       -75 | first payment    | 0357955f-9f2c-493b-9323-fbfea0a25938 |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 12      |        5 |       -70 | daily saving     | saving on Jun 12                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 13      |     -125 |      -195 | groceries        | groceries on Jun 13                  |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 14      |        5 |      -190 | daily saving     | saving on Jun 14                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 16      |        5 |      -185 | daily saving     | saving on Jun 16                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 18      |        5 |      -180 | daily saving     | saving on Jun 18                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 20      |        5 |      -175 | daily saving     | saving on Jun 20                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 20      |     -125 |      -300 | groceries        | groceries on Jun 20                  |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 22      |        5 |      -295 | daily saving     | saving on Jun 22                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 24      |        5 |      -290 | daily saving     | saving on Jun 24                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 26      |        5 |      -285 | daily saving     | saving on Jun 26                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 27      |     -125 |      -410 | groceries        | groceries on Jun 27                  |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 28      |        5 |      -405 | daily saving     | saving on Jun 28                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jun 30      |        5 |      -400 | daily saving     | saving on Jun 30                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 02      |        5 |      -395 | daily saving     | saving on Jul 02                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 04      |        5 |      -390 | daily saving     | saving on Jul 04                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 04      |     -125 |      -515 | groceries        | groceries on Jul 04                  |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 06      |        5 |      -510 | daily saving     | saving on Jul 06                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 08      |        5 |      -505 | daily saving     | saving on Jul 08                     |
+-------------+----------+-----------+------------------+--------------------------------------+
| Jul 10      |        5 |      -500 | daily saving     | saving on Jul 10                     |
+-------------+----------+-----------+------------------+--------------------------------------+
```