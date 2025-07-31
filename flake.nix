# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{
  description = "chat-script Development Environment and Package via Nix Flake";

  nixConfig.bash-prompt = ''\n\[\033[1;31m\][devShell:\w]\$\[\033[0m\] '';

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
              import ./nix/overlay.nix { inherit linux-share darwin-share; }
            );
            deps = (import ./nix/deps.nix { inherit pkgs; });
          }
        );
    in
    {
      devShells = forEachSupportedSystem (import ./nix/shell.nix);
      packages = forEachSupportedSystem (import ./nix/package.nix);
    };
}
