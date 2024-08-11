import pytest
from unittest.mock import patch
from op_brains.setup import main as setup_main


@patch("os.makedirs")
@patch("op_brains.setup.OptimismDocumentProcessorFactory")
@patch("op_brains.setup.DocumentLoader")
def test_setup_main(mock_document_loader, mock_factory, mock_makedirs):
    mock_factory.return_value.get_document_types.return_value = {
        "fragments": "test/path/fragments",
        "forum_posts": "test/path/forum_posts",
    }
    mock_document_loader.return_value.load_documents.return_value = "test_db_path"

    setup_main()

    assert (
        mock_makedirs.call_count >= 3
    )  # BASE_PATH, DB_STORAGE_PATH, and at least one document path
    assert (
        mock_document_loader.return_value.load_documents.call_count == 2
    )  # One for each document type


if __name__ == "__main__":
    pytest.main()
