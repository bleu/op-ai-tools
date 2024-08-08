import pytest
from unittest.mock import Mock, patch
from op_chat_brains.utils import (
    get_rag_model,
    process_question,
    process_question_stream,
)
from op_chat_brains.exceptions import UnsupportedVectorstoreError, OpChatBrainsException


@pytest.fixture
def mock_config():
    return {
        "DEFAULT_DBS": ["test_db1", "test_db2"],
        "EMBEDDING_MODEL": "test_embedding",
        "K_RETRIEVER": 5,
        "VECTORSTORE": "test_vectorstore",
        "PROMPT_BUILDER": lambda x: x,
        "PROMPT_BUILDER_EXPANDER": lambda x: x,
        "CHAT_MODEL_CLAUDE": "claude-test",
        "CHAT_MODEL_OPENAI": "gpt-test",
        "CHAT_TEMPERATURE": 0.7,
        "MAX_RETRIES": 3,
    }


@pytest.fixture
def mock_logger():
    return Mock()


@patch("op_chat_brains.model.RAGSystem.SimpleClaude")
def test_get_rag_model(mock_simple_claude):
    mock_instance = Mock()
    mock_simple_claude.return_value = mock_instance

    result = get_rag_model(
        "claude-simple",
        ["test_db"],
        "test_embedding",
        {"test": "params"},
        "test_vectorstore",
        lambda x: x,
        lambda x: x,
        {"model": "test_model"},
    )
    assert result == mock_instance
    mock_simple_claude.assert_called_once()


def test_get_rag_model_unsupported():
    with pytest.raises(UnsupportedVectorstoreError):
        get_rag_model(
            "unsupported-structure",
            ["test_db"],
            "test_embedding",
            {"test": "params"},
            "test_vectorstore",
            lambda x: x,
            lambda x: x,
            {"model": "test_model"},
        )


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_success(mock_get_rag_model, mock_config, mock_logger):
    mock_rag = Mock()
    mock_rag.predict.return_value = {"answer": "Test answer", "context": "Test context"}
    mock_get_rag_model.return_value = mock_rag

    result = process_question(
        "Test question", "claude-simple", mock_logger, mock_config
    )

    assert result == {"answer": "Test answer", "error": None}
    mock_logger.log_query.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_op_chat_brains_exception(
    mock_get_rag_model, mock_config, mock_logger
):
    mock_get_rag_model.side_effect = OpChatBrainsException("Test error")

    result = process_question(
        "Test question", "claude-simple", mock_logger, mock_config
    )

    assert result == {"answer": None, "error": "Test error"}
    mock_logger.logger.error.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_unexpected_exception(
    mock_get_rag_model, mock_config, mock_logger
):
    mock_get_rag_model.side_effect = Exception("Unexpected error")

    result = process_question(
        "Test question", "claude-simple", mock_logger, mock_config
    )

    assert result == {
        "answer": None,
        "error": "An unexpected error occurred during prediction",
    }
    mock_logger.logger.error.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_stream_success(mock_get_rag_model, mock_config, mock_logger):
    mock_rag = Mock()
    mock_rag.stream.return_value = [
        {"content": "Test "},
        {"content": "answer"},
    ]
    mock_get_rag_model.return_value = mock_rag

    result = list(
        process_question_stream(
            "Test question", "claude-simple", mock_logger, mock_config
        )
    )

    assert result == [
        {"answer": "Test ", "error": None},
        {"answer": "answer", "error": None},
    ]
    mock_logger.log_query.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_stream_unsupported_vectorstore(
    mock_get_rag_model, mock_config, mock_logger
):
    mock_get_rag_model.side_effect = UnsupportedVectorstoreError(
        "Invalid RAG structure"
    )

    result = list(
        process_question_stream(
            "Test question", "invalid-structure", mock_logger, mock_config
        )
    )

    assert result == [
        {"answer": None, "error": "Invalid RAG structure: Invalid RAG structure"}
    ]
    mock_logger.logger.error.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_stream_op_chat_brains_exception(
    mock_get_rag_model, mock_config, mock_logger
):
    mock_get_rag_model.side_effect = OpChatBrainsException("Test error")

    result = list(
        process_question_stream(
            "Test question", "claude-simple", mock_logger, mock_config
        )
    )

    assert result == [{"answer": None, "error": "Test error"}]
    mock_logger.logger.error.assert_called_once()


@patch("op_chat_brains.utils.get_rag_model")
def test_process_question_stream_unexpected_exception(
    mock_get_rag_model, mock_config, mock_logger
):
    mock_get_rag_model.side_effect = Exception("Unexpected error")

    result = list(
        process_question_stream(
            "Test question", "claude-simple", mock_logger, mock_config
        )
    )

    assert result == [
        {"answer": None, "error": "An unexpected error occurred during prediction"}
    ]
    mock_logger.logger.error.assert_called_once()
