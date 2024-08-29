{ pkgs, linux-share, darwin-share, ... }:

(final: prev: {
  python311 = prev.python311.override {
    packageOverrides = python311-final: python311-prev: {
      fastapi = python311-prev.fastapi.overrideAttrs {
        disabledTests = [
          "test_fastapi_cli"
          "test_schema_extra_examples"
        ];
      };
      gradio = python311-prev.gradio.overrideAttrs (old: {
        postInstall = (old.postInstall or "") + ''
          cp -f ${linux-share} $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
          cp -f ${darwin-share} $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
          chmod +x $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
          chmod +x $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
        '';
      });
      langchain-chroma = prev.python311Packages.callPackage ./libs/langchain-chroma {};
      langchain-ollama = prev.python311Packages.callPackage ./libs/langchain-ollama {};
    };
  };
})