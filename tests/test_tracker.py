from fintrack import Tracker, __version__

def test_version():
  assert Tracker().version() == __version__
