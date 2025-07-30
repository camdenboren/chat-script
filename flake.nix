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
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forEachSupportedSystem =
        function:
        nixpkgs.lib.genAttrs supportedSystems (
          system:
          function rec {
            pkgs = nixpkgs.legacyPackages.${system}.extend (
              import ./nix/overlay.nix { inherit pkgs linux-share darwin-share; }
            );
            deps =
              with pkgs.python313Packages;
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
                pyright
                build
                format
              ]
              ++ (with pkgs.python313Packages; [
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

            shellHook = import ./nix/shellHook.nix;
          };
        }
      );
      packages = forEachSupportedSystem (
        { pkgs, deps }:
        {
          default = pkgs.python313Packages.buildPythonApplication {
            pname = "chat-script";
            version = "1.1.0";
            pyproject = true;
            src = ./.;

            build-system = with pkgs.python313Packages; [ setuptools ];
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
