{ pkgs, linux-share, darwin-share, ... }:

(final: prev: {
  python311 = prev.python311.override {
    packageOverrides = python311-final: python311-prev: {
      # Adding disabled test fixes build on darwin due to test_openai_schema failing with: Unclosed <MemoryObjectSendStream>
      fastapi = python311-prev.fastapi.overrideAttrs (old: {
        disabledTests = (old.disabledTests or []) ++ [
          "test_schema_extra_examples"
        ];
      });
      # Fixes share=True by adding necessary files to $out
      gradio = python311-prev.gradio.overrideAttrs (old: {
        postInstall = (old.postInstall or "") + ''
          cp -f ${linux-share} $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
          cp -f ${darwin-share} $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
          chmod +x $out/lib/python3.11/site-packages/gradio/frpc_linux_amd64_v0.2
          chmod +x $out/lib/python3.11/site-packages/gradio/frpc_darwin_arm64_v0.2
        '';
      });
    };
  };
})
