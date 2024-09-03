{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  freezegun,
  langchain-core,
  langchain-standard-tests,
  tiktoken,
  lark,
  ollama,
  pandas,
  poetry-core,
  pytest-asyncio,
  pytest-mock,
  pytest-socket,
  pytestCheckHook,
  pythonOlder,
  requests-mock,
  responses,
  syrupy,
  toml,
}:

buildPythonPackage rec {
  pname = "langchain-ollama";
  version = "0.1.1";
  pyproject = true;

  disabled = pythonOlder "3.8";

  src = fetchFromGitHub {
    owner = "langchain-ai";
    repo = "langchain";
    rev = "refs/tags/langchain-ollama==${version}";
    hash = "sha256-5UAijSTfQ6nQxdZvKHl2o01wDW6+Jphf38V+dAs7Ffk=";
  };

  sourceRoot = "${src.name}/libs/partners/ollama";

  build-system = [ poetry-core ];

  dependencies = [
    langchain-core
    ollama
    tiktoken
  ];

  nativeCheckInputs = [
    freezegun
    langchain-standard-tests
    lark
    pandas
    pytest-asyncio
    pytest-mock
    pytest-socket
    pytestCheckHook
    requests-mock
    responses
    syrupy
    toml
  ];

  pytestFlagsArray = [ "tests/unit_tests" ];

  disabledTests = [
    # These tests require network access
  ];

  pythonImportsCheck = [ "langchain_ollama" ];

  meta = {
    changelog = "https://github.com/langchain-ai/langchain/releases/tag/langchain-ollama==${version}";
    description = "Integration package connecting Ollama and LangChain";
    homepage = "https://github.com/langchain-ai/langchain/tree/master/libs/partners/ollama";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ camdenboren ];
  };
}