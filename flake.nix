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
      pkgs = nixpkgs.legacyPackages.${system};
      deps = with pkgs.python311Packages; [
        chromadb
        (gradio.overrideAttrs (old: {
          postInstall = (old.postInstall or "") + ''
            cp -f ${linux-share} $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
            cp -f ${darwin-share} $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
            chmod +x $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
            chmod +x $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
          '';
        }))
        langchain
        langchain-core
        langchain-community
        (callPackage ./libs/langchain-chroma {})
        (callPackage ./libs/langchain-ollama {})
        tiktoken

        # Seem unnecessary
        #beautifulsoup4

        # Needed for PDF processing - should work once paddlepaddle is updated - also need to rm loader_cls in embeddings()
        #unstructured
        #emoji
        #iso-639
        #langdetect
        #pillow-heif
        #unstructured-inference
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
          echo -e "\nchat-script Development Environment via Nix Flake\n"
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
          mainProgram = "init.py";
        };
      };
    });
  };
}