# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{
  pkgs,
  linux-share,
  darwin-share,
  ...
}:

(final: prev: {
  build = pkgs.callPackage ./build.nix { };
  format = pkgs.callPackage ./format.nix { };
  python313 = prev.python313.override {
    packageOverrides = python313-final: python313-prev: {
      # Fixes share=True by adding necessary files to $out
      gradio = python313-prev.gradio.overrideAttrs (old: {
        disabledTests = (old.disabledTests or [ ]) ++ [
          "test_component_example_values"
          "test_public_request_pass"
          "test_private_request_fail"
          "theme_builder_launches"
        ];
        postInstall =
          (old.postInstall or "")
          + ''
            cp -f ${linux-share} $out/lib/python3.13/site-packages/gradio/frpc_linux_amd64_v0.3
            cp -f ${darwin-share} $out/lib/python3.13/site-packages/gradio/frpc_darwin_arm64_v0.3
            chmod +x $out/lib/python3.13/site-packages/gradio/frpc_linux_amd64_v0.3
            chmod +x $out/lib/python3.13/site-packages/gradio/frpc_darwin_arm64_v0.3
          '';
      });
    };
  };
})
