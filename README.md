# gnome-extensions-cli

Install, update and manage your Gnome Shell extensions from your terminal


# Features

- You can install any extension available on [Gnome website](https://extensions.gnome.org) 
- Automatically select the compatible version to install for your Gnome Shell 
- Automatic Gnome Shell restart if needed
- Simple update command to keep your extensions up-to-date
- You can also uninstall, enable and disable extensions
- Handles extensions installed on the system (with `apt install`) to automatically update them


# Install

Install from [PyPI](https://pypi.org/)
```sh
$ pip3 install --user gnome-extensions-cli
```

Install latest version from the repository
```sh
$ pip3 install --user git+https://github.com/essembeh/gnome-extensions-cli
```

Or setup a development environment
```sh
$ git clone https://github.com/essembeh/gnome-extensions-cli
$ cd gnome-extensions-cli
$ make venv
$ source venv/bin/activate
(venv) $ pip install -e .
```

# Using

## List your extensions

```sh
$ gnome-extensions-cli list
Installed extensions:
[X] dash-to-panel@jderose9.github.com  (v37)
[X] todo.txt@bart.libert.gmail.com  (v25)

# Also include system extensions
$ gnome-extensions-cli list --all
Installed extensions:
[ ] auto-move-windows@gnome-shell-extensions.gcampax.github.com
[X] dash-to-panel@jderose9.github.com  (v37)
[X] todo.txt@bart.libert.gmail.com  (v25)

# Use verbose to see available updates
$ gnome-extensions-cli list -a -v
Installed extensions:
[ ] auto-move-windows@gnome-shell-extensions.gcampax.github.com
      available version: 37
[X] dash-to-panel@jderose9.github.com  (v37)
[X] todo.txt@bart.libert.gmail.com  (v25)
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
      version 25 for Gnome Shell 3.28
      version 25 for Gnome Shell 3.26
      version 25 for Gnome Shell 3.24
      version 25 for Gnome Shell 3.22
      version 25 for Gnome Shell 3.20
      version 25 for Gnome Shell 3.18
      version 25 for Gnome Shell 3.16
      version 25 for Gnome Shell 3.14
      version 25 for Gnome Shell 3.12
      version 25 for Gnome Shell 3.10
      version 21 for Gnome Shell 3.8
      version 21 for Gnome Shell 3.6
      version 21 for Gnome Shell 3.4
```

## Install, uninstall and update

```sh
# Install extension by its UUID
$ gnome-extensions-cli install dash-to-panel@jderose9.github.com
Install Dash to Panel version 37 from https://extensions.gnome.org/download-extension/dash-to-panel@jderose9.github.com.shell-extension.zip?version_tag=16231

# or use its package number from https://extensions.gnome.org
$ gnome-extensions-cli install 1160
Install Dash to Panel version 37 from https://extensions.gnome.org/download-extension/dash-to-panel@jderose9.github.com.shell-extension.zip?version_tag=16231
Restarting Gnome Shell ...

# You can also install multiple extensions
$ gnome-extensions-cli install 1160 570
Install Dash to Panel version 37 from https://extensions.gnome.org/download-extension/dash-to-panel@jderose9.github.com.shell-extension.zip?version_tag=16231
Install Todo.txt version 25 from https://extensions.gnome.org/download-extension/todo.txt@bart.libert.gmail.com.shell-extension.zip?version_tag=8141
Restarting Gnome Shell ...

# Uninstall extensions
$ gnome-extensions-cli uninstall todo.txt@bart.libert.gmail.com                     
Uninstall todo.txt@bart.libert.gmail.com from /home/seb/.local/share/gnome-shell/extensions/todo.txt@bart.libert.gmail.com
Disable todo.txt@bart.libert.gmail.com
Restarting Gnome Shell ...

# You can enable and disable extensions
$ gnome-extensions-cli disable todo.txt@bart.libert.gmail.com
Disable todo.txt@bart.libert.gmail.com
Restarting Gnome Shell ...
$ gnome-extensions-cli enable todo.txt@bart.libert.gmail.com 
Enable todo.txt@bart.libert.gmail.com
Restarting Gnome Shell ...
```

The `update` command by default updates only the *enabled* extensions, use `--all/-a` to also update disabled extensions
```sh
# Update all enabled extensions
$ gnome-extensions-cli update
Extension dash-to-panel@jderose9.github.com is up-to-date
Update todo.txt@bart.libert.gmail.com from 21 to 25

# Update only given extensions
$ gnome-extensions-cli update dash-to-panel@jderose9.github.com is up-to-date
Extension dash-to-panel@jderose9.github.com is up-to-date
```

## 