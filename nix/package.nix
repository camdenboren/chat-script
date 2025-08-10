# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{ pkgs, deps }:

{
  default = pkgs.python313Packages.buildPythonApplication {
    pname = "chat-script";
    version = "1.1.0";
    pyproject = true;
    src = ../.;

    dontCheckRuntimeDeps = true;
    propagatedBuildInputs = deps.build;
    build-system = with pkgs.python313Packages; [ setuptools ];
    postInstall = ''
      mkdir -p $out/docs/img
      cp $src/docs/img/favicon.png $out/docs/img/favicon.png
    '';

    ANONYMIZED_TELEMETRY = "False";

    meta = {
      description = "Chat with your documents using any Ollama LLM with this simple python app";
      maintainers = [ "camdenboren" ];
    };
  };
}
