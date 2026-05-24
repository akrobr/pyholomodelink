import os
import pytest
from pyholomodelink import HoloModeLink

DEVICE_HOST = os.environ.get("HOLOMODELINK_HOST", "localhost")
TEST_VIDEO_PATH = os.environ.get("HOLOMODELINK_TEST_VIDEO", "/work/tests/sample_20Mbps_29.97fps.mp4")


@pytest.fixture(scope="session")
def link():
    return HoloModeLink(host=DEVICE_HOST)


@pytest.fixture(scope="session")
def test_video_path():
    if not TEST_VIDEO_PATH:
        pytest.skip("HOLOMODELINK_TEST_VIDEO not set.")
    if not os.path.exists(TEST_VIDEO_PATH):
        pytest.skip(f"Test video not found: {TEST_VIDEO_PATH}")
    return TEST_VIDEO_PATH