from click.testing import CliRunner
from unittest.mock import patch
from op_chat_brains.cli import main as cli_main


def test_cli_main():
    runner = CliRunner()
    with patch("op_chat_brains.cli.process_question") as mock_process_question:
        mock_process_question.return_value = {
            "answer": "CLI test answer",
            "error": None,
        }
        result = runner.invoke(
            cli_main, ["--rag-structure", "claude-simple", "CLI test question"]
        )
        assert result.exit_code == 0
        assert "CLI test answer" in result.output
