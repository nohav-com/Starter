import platform

from starter.app_preparation_by_platform.linux import LinuxPlatform
from starter.app_preparation_by_platform.platform_handler import \
    PlatformHandler
from starter.app_preparation_by_platform.windows import WindowsPlatform


def test_init():
    """Basic test - initialization."""
    handler_instance = PlatformHandler(
        param_test="param_test"
    )
    # Get handler
    handler = handler_instance.get_handler()
    # Test type - windows platform
    if platform.system().lower() == "windows":
        assert isinstance(handler, WindowsPlatform)
    if platform.system().lower() == "linux":
        assert isinstance(handler, LinuxPlatform)
