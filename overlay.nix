# SPDX-FileCopyrightText: 2024 Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{
  pkgs,
  linux-share,
  darwin-share,
  ...
}:

(final: prev: {
  python312 = prev.python312.override {
    packageOverrides = python312-final: python312-prev: {
      # Fixes share=True by adding necessary files to $out
      gradio = python312-prev.gradio.overrideAttrs (old: {
        disabledTests =
          (old.disabledTests or [ ])
          ++ [
            "test_component_example_values"
            "test_public_request_pass"
            "test_private_request_fail"
            "theme_builder_launches"
          ];
        postInstall =
          (old.postInstall or "")
          + ''
            cp -f ${linux-share} $out/lib/python3.12/site-packages/gradio/frpc_linux_amd64_v0.3
            cp -f ${darwin-share} $out/lib/python3.12/site-packages/gradio/frpc_darwin_arm64_v0.3
            chmod +x $out/lib/python3.12/site-packages/gradio/frpc_linux_amd64_v0.3
            chmod +x $out/lib/python3.12/site-packages/gradio/frpc_darwin_arm64_v0.3
          '';
      });
    };
  };
})
