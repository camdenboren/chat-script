{
  description = "chat-script Development Environment and Package via Nix Flake";

  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
    linux-share = {
      url = "https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_linux_amd64";
      flake = false;
    };
    darwin-share = {
      url = "https://cdn-media.huggingface.co/frpc-gradio-0.2/frpc_darwin_arm64";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, linux-share, darwin-share }: 
  let
    supportedSystems = [ "x86_64-linux" "aarch64-darwin" ];
    forEachSupportedSystem = function: nixpkgs.lib.genAttrs supportedSystems (system: function rec {
      pkgs = nixpkgs.legacyPackages.${system}.extend (import ./overlay.nix {inherit pkgs linux-share darwin-share;});
      deps = with pkgs.python311Packages; [
        gradio
        langchain
        langchain-core
        langchain-community
        langchain-chroma
        langchain-ollama
        notify2
        tiktoken
      ];
    });
  in {
    devShells = forEachSupportedSystem ({ pkgs, deps }: {
      default = pkgs.mkShell {
        packages = with pkgs; [ 
          bashInteractive 
          python311 
        ] ++ (with pkgs.python311Packages; [
          coverage
          mkdocs
          mkdocs-material
          mkdocstrings
          mkdocstrings-python
        ]) ++ deps;

        ANONYMIZED_TELEMETRY = "False";

        shellHook = ''
          echo -e "\nchat-script Development Environment via Nix Flake\n"
          echo -e "run: python -m src.__main__"
          echo -e "test: python -m unittest discover"
          echo -e "cov: coverage run --source=src,test -m unittest discover"
          echo -e "docs: mkdocs build, serve, or gh-deploy\n"
          python --version
        '';
      };
    });
    packages = forEachSupportedSystem ({ pkgs, deps }: {
      default = pkgs.python311Packages.buildPythonApplication {
        pname = "chat-script";
        version = "0.1";
        src = ./.;

        propagatedBuildInputs = deps;

        ANONYMIZED_TELEMETRY = "False";

        meta = {
          description = "Chat locally with scripts (documents) of your choice with this simple python app.";
          maintainers = [ "camdenboren" ];
        };
      };
    });
  };
}
