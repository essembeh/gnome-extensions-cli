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
- You can also uninstall, enable or disable extensions and open preferences

# Install

Install from [PyPI](https://pypi.org/project/gnome-extensions-cli/)

```sh
$ pip3 install --upgrade gnome-extensions-cli
```

Install latest version from the repository

```sh
$ pip3 install --upgrade git+https://github.com/essembeh/gnome-extensions-cli
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

By default, the `list` command only display the _enabled_ extensions, using `-a|--all` argument also displays _disabled_ ones.

![gnome-extensions-cli list](images/list.png)

## Show some details about extensions

The `show` command fetch details from _Gnome website_ and print them.s.

![gnome-extensions-cli show](images/show.png)

## Install, uninstall and update

![gnome-extensions-cli install](images/install.gif)

```sh
# Install extension by its UUID
$ gnome-extensions-cli install dash-to-panel@jderose9.github.com

# or use its package number from https://extensions.gnome.org
$ gnome-extensions-cli install 1160

# You can also install multiple extensions at once
$ gnome-extensions-cli install 1160 todo.txt@bart.libert.gmail.com

# Uninstall extensions
$ gnome-extensions-cli uninstall todo.txt@bart.libert.gmail.com

# You can enable and disable extensions
$ gnome-extensions-cli enable todo.txt@bart.libert.gmail.com
$ gnome-extensions-cli disable todo.txt@bart.libert.gmail.com dash-to-panel@jderose9.github.com
```

The `update` command without arguments updates all _enabled_ extensions.
You can also `update` a specific extension by giving its _uuid_.

![gnome-extensions-cli update](images/update.gif)

> Note: the `--install` argument allow you to _install_ extensions given to `update` command if they are not installed.

## Backends: DBus vs Filesystem

`gnome-extensions-cli` can interact with Gnome Shell using two different implementations, using `dbus` or using a `filesystem` operations:

> Note: By default, it uses `dbus` (as it is the official way), but switches to `filesystem` if `dbus` is not available)

### DBus backend

Using `--dbus`, the application uses _dbus_ messages to communicate with Gnome Shell directly.

Pros:

- You are using the exact same way to install extensions as the Firefox addon
- Automatically restart the Gnome Shell when needed
- Very stable
- You can open the extension preference dialog with `gnome-extensions-cli edit EXTENSION_UUID`

Cons:

- Installations are interactive, you are prompted with a Gnome _Yes/No_ dialog before installing the extensions, so you need to have a running Gnome session

### Filesystem backend

Using `--filesystem`, the application uses unzip packages from [Gnome website](https://extensions.gnome.org) directly in you `~/.local/share/gnome-shell/extensions/` folder, enable/disable them and restarting the Gnome Shell using subprocesses.

Pros:

- You can install extensions without any Gnome session running (usign _ssh_ for example)
- Many `gnome-extensions-cli` alternatives use this method ... but

Cons:

- Some extensions are not installed well
