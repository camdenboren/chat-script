# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{
  linux-share,
  darwin-share,
  ...
}:

(
  final: prev:
  let
    grPath = "$out/lib/python3.13/site-packages/gradio";

    # read script by name and patch bash shebang for nix users
    # see https://ertt.ca/nix/shell-scripts/
    writePatchedScript =
      name:
      (prev.writeScriptBin name (builtins.readFile ../script/${name})).overrideAttrs (old: {
        buildCommand = "${old.buildCommand}\n patchShebangs $out";
      });
  in
  {
    build = writePatchedScript "build";
    format = writePatchedScript "format";
    python313 = prev.python313.override {
      packageOverrides = python313-final: python313-prev: {
        gradio = python313-prev.gradio.overrideAttrs (old: {
          # Fixes share=True by adding necessary files to $out
          postInstall =
            (old.postInstall or "")
            + prev.lib.optionalString prev.stdenv.hostPlatform.isDarwin ''
              cp -f ${darwin-share} ${grPath}/frpc_darwin_arm64_v0.3
              chmod +x ${grPath}/frpc_darwin_arm64_v0.3
            ''
            + prev.lib.optionalString prev.stdenv.hostPlatform.isLinux ''
              cp -f ${linux-share} ${grPath}/frpc_linux_amd64_v0.3
              chmod +x ${grPath}/frpc_linux_amd64_v0.3
            '';
        });
      };
    };
  }
)
