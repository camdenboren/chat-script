# SPDX-FileCopyrightText: Camden Boren
# SPDX-License-Identifier: GPL-3.0-or-later

{ pkgs }:

{
  build =
    with pkgs;
    [
      nodejs
    ]
    ++ (with python313Packages; [
      gradio
      langchain
      langchain-core
      langchain-community
      langchain-chroma
      langchain-ollama
      notify2
      tiktoken
    ]);

  dev =
    with pkgs;
    [
      pyright

      # scripts
      build
      format

      # script deps
      boxes
      nixfmt-rfc-style
      taplo
    ]
    ++ (with python313Packages; [
      coverage
      mkdocs
      mkdocs-material
      mkdocstrings
      mkdocstrings-python
      mockito
      ruff
    ])
    ++ (with nodePackages; [
      # script deps
      prettier
    ]);
}
