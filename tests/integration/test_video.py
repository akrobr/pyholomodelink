import os
import pytest


def test_session_begin_and_end(link):
    link.video.session_end()
    assert link.video.session_begin() is True
    assert link.video.session_end() is True


def test_apply_video(link, test_video_path):
    result = link.video.apply_video(test_video_path)
    assert result.received is True
    assert result.file_name == os.path.basename(test_video_path)
    assert result.recv_file_size == os.path.getsize(test_video_path)


def test_apply_video_file_appears_in_file_list(link, test_video_path):
    link.video.apply_video(test_video_path)
    file_list = link.system.get_file_list()
    assert os.path.basename(test_video_path) in file_list