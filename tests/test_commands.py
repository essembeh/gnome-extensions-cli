from argparse import Namespace
from pathlib import Path

from pytest import CaptureFixture, fixture, raises

from gnome_extensions_cli.commands import disable, enable, install, list_, preferences, search, show, uninstall, update

from .conftest import SAMPLE_UUID, FakeExtensionManager, SampleStore, make_extension


@fixture
def manager(tmp_path: Path) -> FakeExtensionManager:
    installed = [make_extension(tmp_path, SAMPLE_UUID, version=30), make_extension(tmp_path, "other@example.org")]
    return FakeExtensionManager(installed=installed, enabled=[SAMPLE_UUID, "ghost@example.org"])


def update_args(**kwargs: object) -> Namespace:
    args = {"extensions": [], "install": False, "yes": True, "dry_run": False, "user": False}
    args.update(kwargs)
    return Namespace(**args)


def test_list(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    list_.run(Namespace(), manager, sample_store)

    out = capsys.readouterr().out
    assert SAMPLE_UUID in out
    assert "other@example.org" not in out


def test_list_all_only_uuid(
    manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]
) -> None:
    list_.run(Namespace(all=True, only_uuid=True), manager, sample_store)

    assert capsys.readouterr().out.splitlines() == ["other@example.org", SAMPLE_UUID][::-1]


def test_list_verbose(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    list_.run(Namespace(verbose=True, all=True), manager, sample_store)

    out = capsys.readouterr().out
    assert "Gnome Shell" in out
    assert "v45.2" in out
    assert "other@example.org" in out
    assert "ghost@example.org" in out


def test_enable(manager: FakeExtensionManager, sample_store: SampleStore) -> None:
    enable.run(Namespace(uuids=["new@x", "new@x"]), manager, sample_store)

    assert "new@x" in manager.enabled
    assert SAMPLE_UUID in manager.enabled


def test_disable(manager: FakeExtensionManager, sample_store: SampleStore) -> None:
    disable.run(Namespace(uuids=[SAMPLE_UUID], not_installed=False), manager, sample_store)

    assert manager.enabled == ["ghost@example.org"]


def test_disable_not_installed(manager: FakeExtensionManager, sample_store: SampleStore) -> None:
    disable.run(Namespace(uuids=[], not_installed=True), manager, sample_store)

    assert manager.enabled == [SAMPLE_UUID]


def test_uninstall(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    uninstall.run(Namespace(uuids=[SAMPLE_UUID, "missing@x", SAMPLE_UUID]), manager, sample_store)

    assert [e.uuid for e in manager.uninstalled_calls] == [SAMPLE_UUID]
    assert "not installed" in capsys.readouterr().out


def test_preferences(manager: FakeExtensionManager, sample_store: SampleStore) -> None:
    preferences.run(Namespace(uuid=SAMPLE_UUID), manager, sample_store)

    assert [e.uuid for e in manager.edited_calls] == [SAMPLE_UUID]

    with raises(ValueError):
        preferences.run(Namespace(uuid="missing@x"), manager, sample_store)


def test_install_upgrade(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    install.run(Namespace(extensions=["570"]), manager, sample_store)

    assert [e.uuid for e in manager.installed_calls] == [SAMPLE_UUID]
    assert "Upgrade" in capsys.readouterr().out


def test_install_already_installed(tmp_path: Path, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    manager = FakeExtensionManager(installed=[make_extension(tmp_path, SAMPLE_UUID, version=35)], enabled=[SAMPLE_UUID])

    install.run(Namespace(extensions=[SAMPLE_UUID]), manager, sample_store)

    assert manager.installed_calls == []
    assert "already installed" in capsys.readouterr().out


def test_install_enable_only(tmp_path: Path, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    manager = FakeExtensionManager(installed=[make_extension(tmp_path, SAMPLE_UUID, version=35)])

    install.run(Namespace(extensions=[SAMPLE_UUID]), manager, sample_store)

    assert manager.installed_calls == []
    assert manager.enabled == [SAMPLE_UUID]
    assert "Enable" in capsys.readouterr().out


def test_install_not_found(
    manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]
) -> None:
    install.run(Namespace(extensions=["nope"]), manager, sample_store)

    assert manager.installed_calls == []
    assert "Cannot find extension" in capsys.readouterr().out


def test_update(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    update.run(update_args(), manager, sample_store)

    assert [e.uuid for e in manager.installed_calls] == [SAMPLE_UUID]
    assert "outdated" in capsys.readouterr().out


def test_update_dry_run(manager: FakeExtensionManager, sample_store: SampleStore) -> None:
    with raises(SystemExit) as error:
        update.run(update_args(yes=False, dry_run=True), manager, sample_store)

    assert error.value.code == 17
    assert manager.installed_calls == []


def test_update_nothing_to_do(tmp_path: Path, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    manager = FakeExtensionManager(installed=[make_extension(tmp_path, SAMPLE_UUID, version=35)], enabled=[SAMPLE_UUID])

    update.run(update_args(), manager, sample_store)

    assert manager.installed_calls == []
    assert "Nothing to update" in capsys.readouterr().out


def test_update_install_missing(sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    manager = FakeExtensionManager()

    update.run(update_args(extensions=["570"]), manager, sample_store)
    assert manager.installed_calls == []
    assert "not installed" in capsys.readouterr().out

    update.run(update_args(extensions=["570"], install=True), manager, sample_store)
    assert [e.uuid for e in manager.installed_calls] == [SAMPLE_UUID]


def test_show(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    show.run(Namespace(extensions=["570", "nope"], verbose=True), manager, sample_store)

    out = capsys.readouterr().out
    assert SAMPLE_UUID in out
    assert "v35" in out
    assert "v30" in out
    assert "Cannot find extension nope" in out


def test_search(manager: FakeExtensionManager, sample_store: SampleStore, capsys: CaptureFixture[str]) -> None:
    search.run(Namespace(motif=["todo"], limit=0, verbose=False), manager, sample_store)

    out = capsys.readouterr().out
    assert "[1/10]" in out
    assert "[10/10]" in out
    assert SAMPLE_UUID in out
