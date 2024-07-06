import unittest
from unittest.mock import patch, MagicMock
from op_chat_brains.exceptions import OpChatBrainsException
from op_chat_brains.utils import process_question


class TestUtils(unittest.TestCase):
    @patch("op_chat_brains.utils.get_rag_model")
    def test_process_question_success(self, mock_get_rag_model):
        mock_rag = MagicMock()
        mock_rag.predict.return_value = {
            "answer": "Test answer",
            "context": "Test context",
        }
        mock_get_rag_model.return_value = mock_rag

        mock_logger = MagicMock()
        mock_config = {
            "DEFAULT_DBS": ("test_db",),
            "EMBEDDING_MODEL": "test_model",
            "K_RETRIEVER": 5,
            "VECTORSTORE": "test_store",
            "PROMPT_BUILDER": lambda x: x,
            "PROMPT_BUILDER_EXPANDER": lambda x: x,
            "CHAT_MODEL_CLAUDE": "claude",
            "CHAT_MODEL_OPENAI": "gpt",
            "CHAT_TEMPERATURE": 0.5,
            "MAX_RETRIES": 3,
        }

        result = process_question(
            "Test question", "claude-simple", mock_logger, mock_config
        )

        self.assertEqual(result, {"answer": "Test answer", "error": None})
        mock_rag.predict.assert_called_once_with("Test question")
        mock_logger.log_query.assert_called_once()

    @patch("op_chat_brains.utils.get_rag_model")
    def test_process_question_op_chat_brains_exception(self, mock_get_rag_model):
        mock_get_rag_model.side_effect = OpChatBrainsException("Test error")

        mock_logger = MagicMock()
        mock_config = {
            "DEFAULT_DBS": ("test_db",),
            "EMBEDDING_MODEL": "test_model",
            "K_RETRIEVER": 5,
            "VECTORSTORE": "test_store",
            "PROMPT_BUILDER": lambda x: x,
            "PROMPT_BUILDER_EXPANDER": lambda x: x,
            "CHAT_MODEL_CLAUDE": "claude",
            "CHAT_MODEL_OPENAI": "gpt",
            "CHAT_TEMPERATURE": 0.5,
            "MAX_RETRIES": 3,
        }

        result = process_question(
            "Test question", "claude-simple", mock_logger, mock_config
        )

        self.assertEqual(result, {"answer": None, "error": "Test error"})
        mock_logger.logger.error.assert_called_once()


if __name__ == "__main__":
    unittest.main()
