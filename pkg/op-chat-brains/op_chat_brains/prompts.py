def PROMPT_BUILDER(context, question, expanded_question=None):
    return [
        (
            "system",
            f"You are a helpful assistant that provides information about the Optimism Collective. Offer polite and informative answers. Be assertive. Avoid jargon and explain technical terms. Use the following context to answer the question:\n\n{context}",
        ),
        ("human", question),
    ]


def PROMPT_BUILDER_EXPANDER(question):
    return [
        (
            "system",
            "You are a query expansion system for Optimism Governance information retrieval. Expand the user's question to improve search results. Do not answer the question.",
        ),
        ("human", question),
    ]
