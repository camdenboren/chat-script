{
  description = "Python Development Environment via Nix Flake";

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
    });
  in {
    devShells = forEachSupportedSystem ({ pkgs }: {
      default = pkgs.mkShell {
        packages = with pkgs; [ 
          bashInteractive 
          python311 
        ] ++
          (with pkgs.python311Packages; [ 
            langchain
            langchain-core
            langchain-community
            beautifulsoup4
            chromadb
            tiktoken
            sentence-transformers
            gradio
          ]);

        ANONYMIZED_TELEMETRY = "False";

        shellHook = ''
          echo -e "\nPython Development Environment via Nix Flake\n"
          echo -e "Run: python fileName.py\n" 
          python --version
          codium src
        '';
      };
    });
    packages = forEachSupportedSystem ({ pkgs }: {
      default = pkgs.python311Packages.buildPythonApplication {
        pname = "chat-script";
        version = "0.1";

        propagatedBuildInputs = with pkgs.python311Packages; [
          langchain
          langchain-core
          langchain-community
          beautifulsoup4
          chromadb
          tiktoken
          sentence-transformers 
          gradio 
        ];

        src = ./.;

        meta.mainProgram = "app.py";
      };
    });
  };
}