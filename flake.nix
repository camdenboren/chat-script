# SPDX-FileCopyrightText: 2024-2025 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{
  description = "chat-script Development Environment and Package via Nix Flake";

  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    linux-share = {
      url = "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_linux_amd64";
      flake = false;
    };
    darwin-share = {
      url = "https://cdn-media.huggingface.co/frpc-gradio-0.3/frpc_darwin_arm64";
      flake = false;
    };
  };

  outputs =
    {
      nixpkgs,
      linux-share,
      darwin-share,
      ...
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        function:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          function rec {
            pkgs = nixpkgs.legacyPackages.${system}.extend (
              import ./overlay.nix { inherit pkgs linux-share darwin-share; }
            );
            deps =
              with pkgs.python312Packages;
              [
                gradio
                langchain
                langchain-core
                langchain-community
                langchain-chroma
                langchain-ollama
                notify2
                tiktoken
              ]
              ++ (with pkgs; [ nodejs ]);
          }
        );
    in
    {
      devShells = forEachSupportedSystem (
        { pkgs, deps }:
        {
          default = pkgs.mkShell {
            packages =
              with pkgs;
              [
                bashInteractive
                python312
                (writeShellScriptBin "build" ''
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
                '')
                (writeShellScriptBin "format" ''
                  set -e
                  set -o pipefail
                  box() { ${pkgs.boxes}/bin/boxes -d ansi -s $(tput cols); }

                  echo -e "\033[1;33mruff...\033[0m"
                  (ruff check --fix && ruff format) | box

                  echo -e "\n\033[1;33mnix...\033[0m"
                  ${pkgs.nixfmt-rfc-style}/bin/nixfmt flake.nix overlay.nix | box

                  echo -e "\n\033[1;33mprettier...\033[0m"
                  ${pkgs.nodePackages.prettier}/bin/prettier \
                  --plugin=${pkgs.nodePackages.prettier-plugin-toml}\
                  /lib/node_modules/prettier-plugin-toml/lib/index.cjs \
                  --write **/*.yml **/*.md **/*.toml | box
                   
                  echo -e "\n\033[1;32mFormat succeeded.\033[0m"
                '')
              ]
              ++ (with pkgs.python312Packages; [
                coverage
                mkdocs
                mkdocs-material
                mkdocstrings
                mkdocstrings-python
                mockito
                ruff
              ])
              ++ deps;

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
      );
      packages = forEachSupportedSystem (
        { pkgs, deps }:
        {
          default = pkgs.python312Packages.buildPythonApplication {
            pname = "chat-script";
            version = "1.1";
            pyproject = true;
            src = ./.;

            build-system = with pkgs.python312Packages; [ setuptools ];
            propagatedBuildInputs = deps;

            ANONYMIZED_TELEMETRY = "False";

            meta = {
              description = "Chat with your documents using any Ollama LLM with this simple python app";
              maintainers = [ "camdenboren" ];
            };
          };
        }
      );
    };
}
