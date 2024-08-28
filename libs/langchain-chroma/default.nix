{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  freezegun,
  langchain-core,
  langchain-standard-tests,
  tiktoken,
  lark,
  chroma,
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
  pname = "langchain-chroma";
  version = "0.1.2";
  pyproject = true;

  disabled = pythonOlder "3.8";

  src = fetchFromGitHub {
    owner = "langchain-ai";
    repo = "langchain";
    rev = "refs/tags/langchain-chroma==${version}";
    hash = "sha256-5UAijSTfQ6nQxdZvKHl2o01wDW6+Jphf38V+dAs7Ffk=";
  };

  sourceRoot = "${src.name}/libs/partners/chroma";

  build-system = [ poetry-core ];

  dependencies = [
    langchain-core
    chroma
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

  pythonImportsCheck = [ "langchain_chroma" ];

  meta = {
    changelog = "https://github.com/langchain-ai/langchain/releases/tag/langchain-chroma==${version}";
    description = "Integration package connecting Chroma and LangChain";
    homepage = "https://github.com/langchain-ai/langchain/tree/master/libs/partners/chroma";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ camdenboren ];
  };
}