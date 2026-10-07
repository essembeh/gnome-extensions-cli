import io
import json
import os
import subprocess
import zipfile
from pathlib import Path
from re import fullmatch
from shutil import which
from typing import Any

from pytest import CaptureFixture, MonkeyPatch, fixture, mark, raises

from gnome_extensions_cli import filesystem
from gnome_extensions_cli.filesystem import FilesystemExtensionManager
from gnome_extensions_cli.schema import AvailableExtension
from gnome_extensions_cli.store import GnomeExtensionStore

from .conftest import make_extension


class CommandRecorder:
    """
    Fake subprocess layer: records commands, answers with configured outputs and return codes
    """

    def __init__(self) -> None:
        self.calls: list[list[str]] = []
        self.outputs: dict[str, str] = {}
        self.returncodes: dict[str | tuple[str, ...], int] = {}

    def run(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
        self.calls.append(command)
        returncode = self.returncodes.get(tuple(command), self.returncodes.get(command[0], 0))
        if kwargs.get("check") and returncode != 0:
            raise subprocess.CalledProcessError(returncode, command)
        return subprocess.CompletedProcess(command, returncode)

    def check_output(self, command: list[str], **_kwargs: Any) -> str:
        self.calls.append(command)
        if command[0] not in self.outputs:
            raise subprocess.CalledProcessError(1, command)
        return self.outputs[command[0]]


@fixture
def commands(monkeypatch: MonkeyPatch) -> CommandRecorder:
    recorder = CommandRecorder()
    recorder.outputs["gnome-shell"] = "GNOME Shell 45.2\n"
    recorder.outputs["gsettings"] = "@as []\n"
    monkeypatch.setattr(subprocess, "run", recorder.run)
    monkeypatch.setattr(subprocess, "check_output", recorder.check_output)
    monkeypatch.setattr(filesystem, "run", recorder.run)
    return recorder


@fixture
def manager(tmp_path: Path, commands: CommandRecorder) -> FilesystemExtensionManager:
    return FilesystemExtensionManager(
        store=GnomeExtensionStore(),
        user_folder=tmp_path / "user",
        system_folders=[tmp_path / "system", tmp_path / "missing"],
    )


def make_zip(uuid: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("metadata.json", json.dumps({"uuid": uuid, "name": "Sample", "version": 35}))
        archive.writestr("extension.js", "")
    return buffer.getvalue()


@fixture
def downloads(monkeypatch: MonkeyPatch, available_extension: AvailableExtension) -> list[str]:
    urls: list[str] = []

    def urlopen(url: str) -> io.BytesIO:
        urls.append(url)
        return io.BytesIO(make_zip(available_extension.uuid))

    monkeypatch.setattr(filesystem, "urlopen", urlopen)
    return urls


@mark.parametrize(
    ("output", "expected"),
    [
        ("GNOME Shell 45.2\n", "45.2"),
        ("GNOME Shell 3.38.4", "3.38"),
        ("GNOME Shell 49.0", "49.0"),
        ("GNOME Shell 49", "49"),
    ],
)
def test_get_current_shell_version(
    manager: FilesystemExtensionManager, commands: CommandRecorder, output: str, expected: str
) -> None:
    commands.outputs["gnome-shell"] = output

    assert manager.get_current_shell_version() == expected
    assert commands.calls == [["gnome-shell", "--version"]]


def test_get_current_shell_version_unparsable(manager: FilesystemExtensionManager, commands: CommandRecorder) -> None:
    commands.outputs["gnome-shell"] = "whatever"

    with raises(RuntimeError):
        manager.get_current_shell_version()


def test_list_installed_extensions(manager: FilesystemExtensionManager, tmp_path: Path) -> None:
    make_extension(tmp_path / "system", "b@system", version=1)
    make_extension(tmp_path / "system", "a@both", version=1)
    user_ext = make_extension(tmp_path / "user", "a@both", version=2)
    (tmp_path / "user" / "not-an-extension").mkdir()

    installed = manager.list_installed_extensions()

    assert [e.uuid for e in installed] == ["a@both", "b@system"]
    assert installed[0].folder == user_ext.folder
    assert installed[0].metadata.version == 2


def test_list_installed_extensions_empty(manager: FilesystemExtensionManager) -> None:
    assert manager.list_installed_extensions() == []


@mark.parametrize(("output", "expected"), [("@as []\n", []), ("['a@x', 'b@y']\n", ["a@x", "b@y"])])
def test_list_enabled_uuids(
    manager: FilesystemExtensionManager, commands: CommandRecorder, output: str, expected: list[str]
) -> None:
    commands.outputs["gsettings"] = output

    assert manager.list_enabled_uuids() == expected
    assert commands.calls == [["gsettings", "get", "org.gnome.shell", "enabled-extensions"]]


def test_set_enabled_uuids(manager: FilesystemExtensionManager, commands: CommandRecorder) -> None:
    assert manager.set_enabled_uuids(["a@x", "b@y"]) is True

    assert commands.calls[0] == ["gsettings", "set", "org.gnome.shell", "enabled-extensions", '["a@x","b@y"]']
    assert commands.calls[1][0] == "dbus-send"


def test_set_enabled_uuids_failure(
    manager: FilesystemExtensionManager, commands: CommandRecorder, capsys: CaptureFixture[str]
) -> None:
    commands.returncodes["gsettings"] = 1

    assert manager.set_enabled_uuids(["a@x"]) is False
    assert [c[0] for c in commands.calls] == ["gsettings"]
    assert "Error" in capsys.readouterr().err


def test_restart_gnome_shell_failure(
    manager: FilesystemExtensionManager, commands: CommandRecorder, capsys: CaptureFixture[str]
) -> None:
    commands.returncodes["dbus-send"] = 1

    assert manager.restart_gnome_shell() is False
    assert "restart" in capsys.readouterr().err


def test_enable_and_disable_uuids(manager: FilesystemExtensionManager, commands: CommandRecorder) -> None:
    commands.outputs["gsettings"] = "['a@x']\n"

    assert manager.enable_uuids("a@x") is False
    assert manager.enable_uuids("b@y") is True
    assert manager.disable_uuids("unknown@z") is False
    assert manager.disable_uuids("a@x") is True
    assert [c[:2] for c in commands.calls if c[0] == "gsettings" and c[1] == "set"] == [["gsettings", "set"]] * 2


def test_install_extension(
    manager: FilesystemExtensionManager,
    commands: CommandRecorder,
    downloads: list[str],
    available_extension: AvailableExtension,
    tmp_path: Path,
) -> None:
    target = tmp_path / "user" / available_extension.uuid
    target.mkdir(parents=True)
    (target / "old-file").touch()

    assert manager.install_extension(available_extension) is True

    assert downloads == [f"{manager.store.url}{available_extension.download_url}"]
    assert (target / "metadata.json").is_file()
    assert (target / "extension.js").is_file()
    assert not (target / "old-file").exists()
    assert ["gsettings", "set", "org.gnome.shell", "enabled-extensions", f'["{available_extension.uuid}"]'] in (
        commands.calls
    )


def test_install_extension_download_failure(
    manager: FilesystemExtensionManager,
    monkeypatch: MonkeyPatch,
    available_extension: AvailableExtension,
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    def urlopen(_url: str) -> io.BytesIO:
        raise OSError("network down")

    monkeypatch.setattr(filesystem, "urlopen", urlopen)

    assert manager.install_extension(available_extension) is False

    assert not (tmp_path / "user" / available_extension.uuid).exists()
    assert "network down" in capsys.readouterr().err


def test_install_extension_without_download_url(
    manager: FilesystemExtensionManager, available_extension: AvailableExtension
) -> None:
    ext = available_extension.model_copy(update={"download_url": None})

    with raises(ValueError):
        manager.install_extension(ext)


def test_uninstall_extension(manager: FilesystemExtensionManager, commands: CommandRecorder, tmp_path: Path) -> None:
    ext = make_extension(tmp_path / "user", "a@x")
    commands.outputs["gsettings"] = "['a@x']\n"

    manager.uninstall_extension(ext)

    assert not ext.folder.exists()
    assert commands.calls[1][:2] == ["gsettings", "set"]


@mark.skipif(os.geteuid() == 0, reason="root can write anywhere")
def test_uninstall_system_extension(manager: FilesystemExtensionManager, tmp_path: Path) -> None:
    ext = make_extension(tmp_path / "system", "a@x")
    ext.folder.chmod(0o555)
    try:
        with raises(ValueError):
            manager.uninstall_extension(ext)
    finally:
        ext.folder.chmod(0o755)


def test_compile_schemas_nothing_to_do(
    manager: FilesystemExtensionManager, commands: CommandRecorder, tmp_path: Path
) -> None:
    folder = tmp_path / "ext"
    folder.mkdir()
    assert manager.compile_schemas(folder) is True

    (folder / "schemas").mkdir()
    assert manager.compile_schemas(folder) is True

    (folder / "schemas" / "a.gschema.xml").touch()
    (folder / "schemas" / "gschemas.compiled").touch()
    assert manager.compile_schemas(folder) is True

    assert commands.calls == []


def test_compile_schemas(manager: FilesystemExtensionManager, commands: CommandRecorder, tmp_path: Path) -> None:
    folder = tmp_path / "ext"
    (folder / "schemas").mkdir(parents=True)
    (folder / "schemas" / "a.gschema.xml").touch()

    assert manager.compile_schemas(folder) is True
    assert commands.calls == [["glib-compile-schemas", "--version"], ["glib-compile-schemas", "schemas/"]]


def test_compile_schemas_tool_missing(
    manager: FilesystemExtensionManager, commands: CommandRecorder, tmp_path: Path
) -> None:
    folder = tmp_path / "ext"
    (folder / "schemas").mkdir(parents=True)
    (folder / "schemas" / "a.gschema.xml").touch()
    commands.returncodes["glib-compile-schemas"] = 1

    assert manager.compile_schemas(folder) is False
    assert len(commands.calls) == 1


def test_compile_schemas_error(manager: FilesystemExtensionManager, commands: CommandRecorder, tmp_path: Path) -> None:
    folder = tmp_path / "ext"
    (folder / "schemas").mkdir(parents=True)
    (folder / "schemas" / "a.gschema.xml").touch()
    commands.returncodes[("glib-compile-schemas", "schemas/")] = 1

    assert manager.compile_schemas(folder) is False
    assert len(commands.calls) == 2


@mark.skipif(which("gnome-shell") is None, reason="gnome-shell is not installed")
def test_live_filesystem_backend() -> None:
    manager = FilesystemExtensionManager(store=GnomeExtensionStore())

    assert fullmatch(r"[0-9]+(\.[0-9]+)?", manager.get_current_shell_version())
    assert all(e.metadata_json.is_file() for e in manager.list_installed_extensions())
