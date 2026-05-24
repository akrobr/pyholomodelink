import pytest
from unittest.mock import patch

from pyholomodelink.commands.system import SystemCommand
from pyholomodelink.exceptions import (
    GetBrightnessError,
    SetBrightnessError,
    GetFileListError,
    RecvStatusError,
)


def test_get_brightness_returns_value(mock_client):
    mock_client.send_cmd.return_value = "[get_bl][50]"
    result = SystemCommand(mock_client).get_brightness()
    mock_client.send_cmd.assert_called_once_with("[get_bl]")
    assert result == "50"


def test_get_brightness_raises_on_no_response(mock_client):
    mock_client.send_cmd.return_value = ""
    with pytest.raises(GetBrightnessError):
        SystemCommand(mock_client).get_brightness()


def test_get_brightness_returns_none_on_unexpected_response(mock_client):
    mock_client.send_cmd.return_value = "[unknown][response]"
    assert SystemCommand(mock_client).get_brightness() is None


def test_set_brightness_returns_value(mock_client):
    mock_client.send_cmd.return_value = "[set_bl][80]"
    result = SystemCommand(mock_client).set_brightness(80)
    mock_client.send_cmd.assert_called_once_with("[set_bl][80]")
    assert result == "80"


def test_set_brightness_raises_on_no_response(mock_client):
    mock_client.send_cmd.return_value = ""
    with pytest.raises(SetBrightnessError):
        SystemCommand(mock_client).set_brightness(80)


def test_get_file_list_returns_list(mock_client):
    mock_client.send_cmd.return_value = "[get_file_list][file1.mp4,file2.mp4]"
    result = SystemCommand(mock_client).get_file_list()
    assert result == ["file1.mp4", "file2.mp4"]


def test_get_file_list_raises_on_no_response(mock_client):
    mock_client.send_cmd.return_value = ""
    with pytest.raises(GetFileListError):
        SystemCommand(mock_client).get_file_list()


def test_get_file_list_raises_on_unexpected_response(mock_client):
    mock_client.send_cmd.return_value = "[unknown][response]"
    with pytest.raises(GetFileListError):
        SystemCommand(mock_client).get_file_list()


def test_iter_recv_status_yields_until_received(mock_client):
    mock_client.send_cmd.side_effect = [
        "[get_file_list][file.mp4,500000]",
        "[get_file_list][file.mp4,1000000]",
    ]
    with patch("time.sleep"):
        statuses = list(SystemCommand(mock_client).iter_recv_status("file.mp4", 1000000))
    assert statuses[-1].received is True


def test_iter_recv_status_raises_on_timeout(mock_client):
    mock_client.send_cmd.return_value = "[get_file_list][file.mp4,0]"
    with patch("time.sleep"):
        with pytest.raises(RecvStatusError):
            list(SystemCommand(mock_client).iter_recv_status("file.mp4", 1000000, tout=0))
