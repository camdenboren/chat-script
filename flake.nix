{
  description = "chat-script Development Environment and Package via Nix Flake";

  inputs = {
    nixpkgs = {
      url = "github:nixos/nixpkgs/nixos-unstable";
    };
  };

  outputs = { self, nixpkgs }: 
  let
    supportedSystems = [ "x86_64-linux" "aarch64-linux" "aarch64-darwin" ];
    forEachSupportedSystem = function: nixpkgs.lib.genAttrs supportedSystems (system: function {
      pkgs = nixpkgs.legacyPackages.${system};
      deps = with nixpkgs.legacyPackages.${system}.python311Packages; [
        langchain
        langchain-core
        langchain-community
        beautifulsoup4
        chromadb
        tiktoken
        sentence-transformers
        gradio
      ];
    });
  in {
    devShells = forEachSupportedSystem ({ pkgs, deps }: {
      default = pkgs.mkShell {
        packages = with pkgs; [ 
          bashInteractive 
          python311 
        ] ++ deps;

        ANONYMIZED_TELEMETRY = "False";

        shellHook = ''
          echo -e "\nchat-script Development Environment and Package via Nix Flake\n"
          echo -e "Run: python fileName.py\n" 
          python --version
          codium src
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

        meta.mainProgram = "app.py";
      };
    });
  };
}