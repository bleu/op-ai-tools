def model_predicted_answer(answer: str) -> bool:
    """
    Determines whether the provided answer is a valid prediction or a fallback response.

    Args:
        answer (str): The answer string produced by the model.

    Returns:
        bool: `True` if the answer is a valid prediction, `False` otherwise.
    """
    if "I'm sorry, but I can only answer questions about" in answer:
        return False

    return True
