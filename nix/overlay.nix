# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

final: prev:
let
  # read script by name and patch bash shebang for nix users
  # see https://ertt.ca/nix/shell-scripts/
  writePatchedScript =
    name:
    (prev.writeScriptBin name (builtins.readFile ../script/${name})).overrideAttrs (old: {
      buildCommand = "${old.buildCommand}\n patchShebangs $out";
    });
in
{
  build = writePatchedScript "build";
  format = writePatchedScript "format";
}
