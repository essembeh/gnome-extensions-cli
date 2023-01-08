![Github](https://img.shields.io/github/tag/essembeh/gnome-extensions-cli.svg)
![PyPi](https://img.shields.io/pypi/v/gnome-extensions-cli.svg)
![Python](https://img.shields.io/pypi/pyversions/gnome-extensions-cli.svg)
![CI](https://github.com/essembeh/gnome-extensions-cli/actions/workflows/poetry.yml/badge.svg)

# gnome-extensions-cli

Install, update and manage your Gnome Shell extensions from your terminal

# Features

- You can install any extension available on [Gnome website](https://extensions.gnome.org)
- Use _DBus_ to communicate with _Gnome Shell_ like the Firefox addon does
  - Also support non-DBus installations if needed
- Automatically select the compatible version to install for your Gnome Shell
- Automatic Gnome Shell restart if needed
- Update all your extensions with one command: `gnome-extensions-cli update`
- You can also uninstall, enable and disable extensions and open preferences

# Install

Install from [PyPI](https://pypi.org/project/gnome-extensions-cli/)

```sh
$ pip3 install -u gnome-extensions-cli
```

Install latest version from the repository

```sh
$ pip3 install -u git+https://github.com/essembeh/gnome-extensions-cli
```

Or setup a development environment

```sh
# dependencies to install PyGObject with pip
$ sudo apt install libgirepository1.0-dev gcc libcairo2-dev pkg-config python3-dev gir1.2-gtk-3.0

# clone the repository
$ git clone https://github.com/essembeh/gnome-extensions-cli
$ cd gnome-extensions-cli

# create the venv using poetry
$ poetry install
$ poetry shell
(venv) $ gnome-extensions-cli --help
```

# Using

## List your extensions

```sh
$ gnome-extensions-cli list
Installed extensions:
[ ] auto-move-windows@gnome-shell-extensions.gcampax.github.com
[X] dash-to-panel@jderose9.github.com (v37)
[X] todo.txt@bart.libert.gmail.com (v25)

# Use verbose to see available updates
$ gnome-extensions-cli list -v
Installed extensions:
[ ] auto-move-windows@gnome-shell-extensions.gcampax.github.com
      available version: 37
[X] dash-to-panel@jderose9.github.com (v37)
[X] todo.txt@bart.libert.gmail.com (v25)
```

> Note: the first `[X]` or `[ ]` indicates if the extension is enabled or not

You also have a `search` command to print informations from Gnome extensions website

```sh
$ gnome-extensions-cli search 570
Todo.txt: todo.txt@bart.libert.gmail.com
    url: https://extensions.gnome.org/extension/570
    tag: 8141
    recommended version: 25
    installed version: 25
    available versions:
      version 30 for Gnome Shell 3.36
      version 29 for Gnome Shell 3.34
      version 28 for Gnome Shell 3.32
      [...]
```

## Install, uninstall and update

```sh
# Install extension by its UUID
$ gnome-extensions-cli install dash-to-panel@jderose9.github.com

# or use its package number from https://extensions.gnome.org
$ gnome-extensions-cli install 1160

# You can also install multiple extensions at once
$ gnome-extensions-cli install 1160 570

# Uninstall extensions
$ gnome-extensions-cli uninstall todo.txt@bart.libert.gmail.com
# ... or use extension number
$ gnome-extensions-cli uninstall 570

# You can enable and disable extensions
$ gnome-extensions-cli disable todo.txt@bart.libert.gmail.com dash-to-panel@jderose9.github.com
$ gnome-extensions-cli enable todo.txt@bart.libert.gmail.com
# equivalent to
$ gnome-extensions-cli disable 570 1160
$ gnome-extensions-cli enable 570
```

The `update` command by default updates only the _enabled_ extensions, use `--all/-a` to also update disabled extensions

```sh
# Update all enabled extensions
$ gnome-extensions-cli update

# Update only given extensions
$ gnome-extensions-cli update dash-to-panel@jderose9.github.com
# ... or use extension number
$ gnome-extensions-cli update 1160
```

## Backends: DBus vs File

`gnome-extensions-cli` can interact with Gnome Shell using two different implementations, using `dbus` or using a `file` based way:

> By default, it uses `dbus` which is the safest way ;)

### DBus

Using `--backend dbus`, the application uses _dbus_ messages to communicate with Gnome Shell directly.

Pros:

- You are using the exact same way to install extensions as the Firefox addon
- Automatically restart the Gnome Shell when needed
- Very stable
- You can open the extension preference dialog with `gnome-extensions-cli edit EXTENSION1_UUID`
  Cons:
- Installations are interactive, you are prompted with e Gnome Yes/No dialog before installing the extensions, so you need to have a running Gnome sessions

### File

Using `--backend dbus`, the application uses unzip packages from [Gnome website](https://extensions.gnome.org) directly in you `~/.local/share/gnome-shell/extensions/` folder, enable/disable them and restarting the Gnome Shell using subprocesses.

Pros:

- You can install extensions without any Gnome session running
- Many `gnome-extensions-cli` alternatives use this method ... but
  Cons:
- Some extensions are not installed well
