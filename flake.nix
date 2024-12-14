# SPDX-FileCopyrightText: 2024 Camden Boren
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
      self,
      nixpkgs,
      linux-share,
      darwin-share,
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
              ++ (with pkgs; [
                nodejs
              ]);
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
              ]
              ++ (with pkgs.python312Packages; [
                coverage
                mkdocs
                mkdocs-material
                mkdocstrings
                mkdocstrings-python
                mockito
              ])
              ++ deps;

            ANONYMIZED_TELEMETRY = "False";

            shellHook = ''
              echo -e "\nchat-script Development Environment via Nix Flake\n"
              echo -e "run:  python -m src"
              echo -e "test: python -m unittest discover"
              echo -e "cov:  coverage run --source=src,test -m unittest discover"
              echo -e "docs: mkdocs build, serve, or gh-deploy\n"
              python --version
            '';
          };
        }
      );
      packages = forEachSupportedSystem (
        { pkgs, deps }:
        {
          default = pkgs.python312Packages.buildPythonApplication {
            pname = "chat-script";
            version = "1.0";
            src = ./.;

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
