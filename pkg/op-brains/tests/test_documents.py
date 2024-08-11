import pytest
from unittest.mock import Mock, mock_open, patch
from op_brains.documents import (
    DocumentLoader,
)
from op_brains.documents.optimism import (
    ForumPostsProcessingStrategy,
    FragmentsProcessingStrategy,
    OptimismDocumentProcessorFactory,
)


def test_forum_posts_processing_strategy():
    strategy = ForumPostsProcessingStrategy()
    assert strategy.get_db_name() == "posts_forum_db"


def test_optimism_document_processor_factory():
    factory = OptimismDocumentProcessorFactory()
    assert isinstance(
        factory.create_processor("fragments"), FragmentsProcessingStrategy
    )
    assert isinstance(
        factory.create_processor("forum_posts"), ForumPostsProcessingStrategy
    )
    with pytest.raises(ValueError):
        factory.create_processor("invalid_type")


@patch("op_brains.documents.FAISS")
@patch("op_brains.documents.OpenAIEmbeddings")
def test_document_loader(mock_embeddings, mock_faiss):
    factory = OptimismDocumentProcessorFactory()
    loader = DocumentLoader(factory)
    mock_faiss.from_documents.return_value = Mock()
    mock_faiss.from_documents.return_value.save_local = Mock()

    mock_file_content = (
        "==> test/file <==\nTest content\n==> another/file <==\nMore content"
    )
    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        loader.load_documents("fragments", "test_file_path")

    mock_faiss.from_documents.assert_called_once()
    mock_faiss.from_documents.return_value.save_local.assert_called_once()


def test_fragments_processing_strategy():
    strategy = FragmentsProcessingStrategy()
    mock_file_content = (
        "==> test/file <==\nTest content\n==> another/file <==\nMore content"
    )

    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        documents = strategy.process_document("test_file_path")

    assert len(documents) == 2
    assert documents[0].page_content.strip() == "Test content"
    assert documents[1].page_content.strip() == "More content"
    assert documents[0].metadata["document_name"] == "file"
    assert documents[1].metadata["document_name"] == "file"
