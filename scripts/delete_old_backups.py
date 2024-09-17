"""Script to delete old backups in Azure.

Tests builtin, just run `pytest` on this file.
"""

import re
import sys
from pathlib import Path
from datetime import date




MAX_LIFE = 30  # days
RE_BACKUP_FILENAME = r"backupOn(\d\d\d\d)-(\d\d)-(\d\d)-(\d\d)-00_.*\.dump"

today = date.today()


def remove_old_files(basedir):
    """Remove (some) old files found in the indicated directory.

    The rule to deletion is: all those files older than MAX_LIFE days except first month day.
    """
    allfiles = basedir.iterdir()
    for fpath in allfiles:
        if rematch := re.match(RE_BACKUP_FILENAME, str(fpath.name)):
            year, month, day, hour = map(int, rematch.groups())
            if day == 1 and hour == 0:
                # do not remove backups from first day of month
                continue
            backup_date = date(year, month, day)
            delta_days = (today - backup_date).days
            if delta_days > MAX_LIFE:
                # too old! remove it
                fpath.unlink()

if __name__ == "__main__":
    remove_old_files(Path("/pg_backup/"))
    sys.exit(0)
else:
    # import pytest only when this is used as a module (imported by pytest itself to run the tests)
    import pytest


def test_nothing(tmp_path):
    """No files in the indicated directory."""
    remove_old_files(tmp_path)


@pytest.mark.parametrize("filedate", [
    "2001-11-08",  # today
    "2001-11-07",  # yesterday
    "2002-11-07",  # next year ... impossible, but let's test it anyway
    "2001-10-09",  # exactly MAX_LIFE ago
])
@pytest.mark.parametrize("descriptor", [
    "eventol_prod",
    "web_production",
    "asoc_members",
])
def test_recent(tmp_path, filedate, descriptor, monkeypatch):
    """Do not remove recent files."""
    testfile = tmp_path / f"backupOn{filedate}-00-00_{descriptor}.dump"
    testfile.touch()
    monkeypatch.setitem(globals(), "today", date(2001, 11, 8))
    remove_old_files(tmp_path)
    assert testfile.exists()


@pytest.mark.parametrize("filedate", [
    "2001-10-08",  # a month ago... but it's actually 31 days!
    "2001-10-02",  # little older than the limit
    "2001-02-15",  # quite older
])
@pytest.mark.parametrize("descriptor", [
    "eventol_prod",
    "web_production",
    "asoc_members",
])
def test_older_normal(tmp_path, filedate, descriptor, monkeypatch):
    """Remove old files."""
    testfile = tmp_path / f"backupOn{filedate}-00-00_{descriptor}.dump"
    testfile.touch()
    monkeypatch.setitem(globals(), "today", date(2001, 11, 8))
    remove_old_files(tmp_path)
    assert not testfile.exists()


@pytest.mark.parametrize("filedate", [
    "2001-11-01",  # day one same month
    "2001-10-01",  # day one previous month
    "2000-01-01",  # day one, really old
])
def test_older_firstday(tmp_path, filedate, monkeypatch):
    """Keep files for day one no matter if old."""
    testfile = tmp_path / f"backupOn{filedate}-00-00_eventol_prod.dump"
    testfile.touch()
    monkeypatch.setitem(globals(), "today", date(2001, 11, 8))
    remove_old_files(tmp_path)
    assert testfile.exists()


def test_complete(tmp_path, monkeypatch):
    """Normal case, lot of files, some to keep some to don't."""
    # pairs date / should still exist
    testpoints = [
        ("2001-09-01", True),
        ("2001-09-05", False),
        ("2001-09-15", False),
        ("2001-10-01", True),
        ("2001-10-05", False),
        ("2001-10-15", True),
        ("2001-11-01", True),
        ("2001-11-05", True),
    ]

    testfiles = []
    for filedate, keep in testpoints:
        tf = tmp_path / f"backupOn{filedate}-00-00_eventol_prod.dump"
        tf.touch()
        testfiles.append((tf, keep))
    monkeypatch.setitem(globals(), "today", date(2001, 11, 8))
    remove_old_files(tmp_path)

    for tf, keep in testfiles:
        assert tf.exists() == keep
