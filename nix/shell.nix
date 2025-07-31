# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{ pkgs, deps }:

{
  default = pkgs.mkShell {
    packages = deps.build ++ deps.dev;

    ANONYMIZED_TELEMETRY = "False";

    shellHook = ''
      echo -e "\nchat-script Development Environment via Nix Flake\n"

      echo -e "┌───────────────────────────────────────────────┐"
      echo -e "│                Useful Commands                │"
      echo -e "├──────────┬────────────────────────────────────┤"
      echo -e "│ Build    │ $ build                            │"
      echo -e "│ Run      │ $ python -m src.chat_script        │"
      echo -e "│ Test     │ $ python -m unittest               │"
      echo -e "│ Format   │ $ format                           │"
      echo -e "│ Coverage │ $ coverage run -m unittest         │"
      echo -e "│ Docs     │ $ mkdocs {build, serve, gh-deploy} │"
      echo -e "└──────────┴────────────────────────────────────┘\n"
    '';
  };
}
