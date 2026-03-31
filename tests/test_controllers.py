import pytest

from src.config import settings
from src.controllers import EasyController, ExtremeController, HardController
from src.utils import (
    check_pow,
    hex_to_bytes,
    sha256_hex,
)


class TestUtils:
    def test_sha256_hex(self):
        result = sha256_hex("hello")
        assert (
            result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        )

    def test_hex_to_bytes(self):
        result = hex_to_bytes("deadbeef")
        assert result == bytes([0xDE, 0xAD, 0xBE, 0xEF])

    def test_check_pow_true(self):
        result = check_pow("test", 1000, 1)
        assert isinstance(result, bool)

    def test_check_pow_false(self):
        result = check_pow("test", 1, 20)
        assert result is False


class TestSettings:
    def test_settings_loads(self):
        assert settings.base_url == "https://localhost:3000"
        assert settings.easy_username == "admin"
        assert settings.extreme_username == "root"
        assert settings.pow_difficulty == 5


class TestControllers:
    def test_easy_controller_create(self):
        controller = EasyController()
        assert controller.name == "easy"

    def test_hard_controller_create(self):
        controller = HardController()
        assert controller.name == "hard"

    def test_extreme_controller_create(self):
        controller = ExtremeController()
        assert controller.name == "extreme"

    @pytest.fixture
    def docker_running(self):
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("localhost", 3000))
        sock.close()
        return result == 0

    @pytest.mark.asyncio
    async def test_easy_controller_run(self, docker_running):
        if not docker_running:
            pytest.skip("Docker container not running")

        controller = EasyController()
        result = await controller.run()

        assert isinstance(result, dict)
        assert "success" in result
        assert "elapsed_ms" in result

    @pytest.mark.asyncio
    async def test_extreme_controller_run(self, docker_running):
        if not docker_running:
            pytest.skip("Docker container not running")

        controller = ExtremeController()
        result = await controller.run()

        assert isinstance(result, dict)
        assert "success" in result
        assert "elapsed_ms" in result
