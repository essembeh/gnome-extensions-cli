# Dev shell: PyGObject (gi) cannot be pip-installed on NixOS, so Nix provides it
# and the uv venv is created with --system-site-packages (see .envrc).
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = [
    (pkgs.python312.withPackages (p: [ p.pygobject3 ]))
    pkgs.gobject-introspection
  ];
}
