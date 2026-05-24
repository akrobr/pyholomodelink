import pytest


def test_get_bl(link):
    result = link.system.get_bl()
    assert isinstance(result, int)
    assert 0 <= result <= 100


def test_set_bl(link):
    original = link.system.get_bl()

    link.system.set_bl(50)
    assert link.system.get_bl() == 50

    link.system.set_bl(original)
    assert link.system.get_bl() == original


def test_get_file_list(link):
    result = link.system.get_file_list()
    assert isinstance(result, list)


def test_get_version(link):
    result = link.system.get_version()
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_datetime(link):
    result = link.system.get_datetime()
    assert isinstance(result, str)
    assert len(result) == 15  # YYYYMMDD-HHMMSS


def test_set_datetime(link):
    original = link.system.get_datetime()

    link.system.set_datetime(original)
    assert link.system.get_datetime() == original


def test_get_clock_display(link):
    result = link.system.get_clock_display()
    assert isinstance(result, dict)
    assert "enable" in result
    assert "color" in result
    assert "y_offset" in result


def test_set_clock_display(link):
    original = link.system.get_clock_display()

    link.system.set_clock_display(
        enable=original["enable"],
        color=original["color"],
        y_offset=original["y_offset"]
    )
    result = link.system.get_clock_display()
    assert result == original


def test_iter_reboot(link):
    statuses = list(link.system.iter_reboot())
    assert len(statuses) > 0
    assert statuses[-1].can_connect is True
    assert statuses[-1].status == "Rebooted"