import unittest
from unittest.mock import patch
from op_chat_brains.api import app
from op_chat_brains.exceptions import UnsupportedVectorstoreError


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("op_chat_brains.utils.get_rag_model")
    def test_predict(self, mock_get_rag_model):
        mock_rag = unittest.mock.Mock()
        mock_rag.predict.return_value = {
            "answer": "Test answer",
            "context": "Test context",
        }
        mock_get_rag_model.return_value = mock_rag

        response = self.app.post("/predict", json={"question": "Test question"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["answer"], "Test answer")
        mock_rag.predict.assert_called_once_with("Test question")

    def test_predict_no_question(self):
        response = self.app.post("/predict", json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "No question provided")

    @patch("op_chat_brains.utils.get_rag_model")
    def test_predict_value_error(self, mock_get_rag_model):
        mock_get_rag_model.side_effect = UnsupportedVectorstoreError(
            "Invalid RAG structure"
        )
        response = self.app.post(
            "/predict", json={"question": "Test question", "rag_structure": "invalid"}
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "Invalid RAG structure")

    @patch("op_chat_brains.utils.get_rag_model")
    def test_predict_unexpected_error(self, mock_get_rag_model):
        mock_get_rag_model.side_effect = Exception("Unexpected error")
        response = self.app.post("/predict", json={"question": "Test question"})
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertEqual(
            data["error"], "An unexpected error occurred during prediction"
        )


if __name__ == "__main__":
    unittest.main()
