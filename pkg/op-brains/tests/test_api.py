import pytest
from unittest.mock import patch
from op_brains.api import app
from op_brains.exceptions import UnsupportedVectorstoreError


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@patch("op_brains.api.process_question")
def test_predict_value_error(mock_process_question, client):
    mock_process_question.side_effect = UnsupportedVectorstoreError(
        "Invalid RAG structure"
    )
    response = client.post(
        "/predict", json={"question": "Test question", "rag_structure": "invalid"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Invalid RAG structure"


@patch("op_brains.api.process_question")
def test_predict_unexpected_error(mock_process_question, client):
    mock_process_question.side_effect = Exception("Unexpected error")
    response = client.post("/predict", json={"question": "Test question"})
    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "An unexpected error occurred during prediction"


# Updated CLI test
@patch("op_brains.cli.process_question")
def test_cli_main(mock_process_question, capsys):
    mock_process_question.return_value = {"answer": "CLI test answer", "error": None}
    with pytest.raises(SystemExit) as excinfo:
        from op_brains.cli import main as cli_main

        cli_main(["--rag-structure", "claude-simple", "CLI test question"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "CLI test answer" in captured.out
