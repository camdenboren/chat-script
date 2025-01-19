# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{ pkgs }:

pkgs.writeShellScriptBin "build" ''
  set -e
  set -o pipefail
  box() { ${pkgs.boxes}/bin/boxes -d ansi -s $(tput cols); }

  echo -e "\033[1;33mruff...\033[0m"
  ruff check | box

  echo -e "\n\033[1;33mcoverage...\033[0m"
  coverage run -m unittest 2> /dev/null | box

  echo -e "\n\033[1;33mbuild...\033[0m"
  nix build 2> /dev/null | box

  echo -e "\n\033[1;32mBuild succeeded.\033[0m"
''
