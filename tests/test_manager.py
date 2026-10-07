from .conftest import FakeExtensionManager


def test_enable_uuids() -> None:
    manager = FakeExtensionManager(enabled=["a@x"])

    assert manager.enable_uuids("a@x") is False
    assert manager.enable_uuids("a@x", "b@y") is True
    assert sorted(manager.enabled) == ["a@x", "b@y"]


def test_disable_uuids() -> None:
    manager = FakeExtensionManager(enabled=["a@x", "b@y"])

    assert manager.disable_uuids("unknown@z") is False
    assert manager.disable_uuids("a@x", "unknown@z") is True
    assert manager.enabled == ["b@y"]
