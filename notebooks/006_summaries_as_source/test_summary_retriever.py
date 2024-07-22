import streamlit as st
import model_builder, time

from datetime import date
TODAY = date.today()

with st.echo():
    from langchain_openai import OpenAIEmbeddings
    embedding_model = "text-embedding-ada-002"
    chat_pars = {
        "temperature": 0.0,
        "max_retries": 5,
        "max_tokens": 1024,
        "timeout": 60,
    }
    dbs = ["summaries"]
    from langchain_community.vectorstores import FAISS
    vectorstore = 'faiss'
    reasoning_limit = 3

chat_models_openai = ["gpt-3.5-turbo-0125", "gpt-4o"]
chat_models_anthropic = ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229", "claude-3-5-sonnet-20240620"]
all_models = chat_models_openai + chat_models_anthropic
chosen_model = st.selectbox("Select chat model", all_models, index=1)
chat_pars["model"] = chosen_model

if chosen_model in chat_models_openai:
    llm_type = "openai"
elif chosen_model in chat_models_anthropic:
    llm_type = "claude"

archs = [
    "simple",
    "multi_retriever",
    "contextual_compression",
    "query_expansion",
]

structure = st.selectbox("Select architecture", archs, index=0)


with st.echo():
    match structure:
        case "simple":
                k = 5 # number of context elements
                retriever_pars = {
                    "search_kwargs" : {'k': k+1}
                }

                prompt_template = lambda question, context: [
                    (
                        "system",
                        f"""
You are a helpful assistant that provides information about Optimism Governance. Your goal is to give polite, informative, assertive, objective, and brief answers. Avoid jargon and explain any technical terms, as the user may not be a specialist.

You will be provided with the following inputs:
<context>
{{CONTEXT}}
</context>

<question>
{{USER_QUESTION}}
<question>

Today's date is {TODAY}. Be aware of information that might be outdated.

Follow these steps:

1. Analyze the user's question and the provided context.

2. List briefly what the user seems to want to know inside <things_to_answer> tags.

3. Check if you have enough information in the context to answer those questions.

4. If you think more information is necessary to fully answer the query, provide related questions that should be clarified inside <need_to_know> tags. Try to expand the user's query to allow for a new improved search. In this case, do not provide an answer. Don't comment on the context or the question, just list every piece of information that you think would be necessary to completely answer the user's query. The user can ask for more information later. So, there is no need to provide a complete answer if there is already useful information in the context.

5. Some questions can have a temporal aspect. For example:
- If the user wants to know about the current status of something.
- If the user wants to know the last time something happened).
In these cases: consider always that today's date is {TODAY}. Always be cautious about afirming stuff. If you think more recent information is necessary, you think more information is necessary. Mention what type of recent information could be useful in the <need_to_know> tags. Do not provide an answer in this case.

6. If you have enough information to respond at least partially the question, provide an answer inside <answer> tags. Your answer should:
   - Directly address the user's question without saying "according to the context", "based on the provided context" or similar phrases.
   - Cite the source URL using the format [1] within the text.
   - List the url references at the end of the answer.
   - Be polite, informative, assertive, objective, and brief.
   - Avoid jargon and explain any technical terms.

7. Format your entire response as follows:
   <things_to_answer>
   [List of things the user wants to know]
   </things_to_answer>

   [Either the <need_to_know> section if there's insufficient information, or:]

   <answer>
   [Your answer here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </answer>

Remember to be helpful, polite, and informative while maintaining assertiveness, objectivity, and brevity in your response.
"""
                    ),
                    (
                        "human",
                        f"<question> {question} </question> \n\n <context> {context} </context>"
                    )
                ]

                final_prompt_template = lambda question, context: [
                    (
                        "system",
                        f"""
You are a helpful assistant that provides information about Optimism Governance. Your goal is to give polite, informative, assertive, objective, and brief answers. Avoid jargon and explain any technical terms, as the user may not be a specialist.

You will be provided with the following inputs:
<context>
{{CONTEXT}}
</context>

<question>
{{USER_QUESTION}}
<question>

Today's date is {TODAY}. Be aware of information that might be outdated.

Follow these steps:

1. Analyze the user's question and the provided context.

2. List briefly what the user seems to want to know inside <things_to_answer> tags.

3. Check if you have enough information in the context to answer those questions.

4. If you have enough information, provide an answer inside <answer> tags. Your answer should:
   - Directly address the user's question without saying "according to the context" or similar phrases.
   - Cite the source URL using the format [1] within the text.
   - List the url references at the end of the answer.
   - Be polite, informative, assertive, objective, and brief.
   - Avoid jargon and explain any technical terms.

5. If you don't have enough information, start the <answer> tag with "I couldn't find all the information I wanted to provide a complete answer." And provide some context about the information you found an what you think is missing to properly answer the user's query.

6. Format your entire response as follows:
   <things_to_answer>
   [List of things the user wants to know]
   </things_to_answer>

   <answer>
   [Your answer here, with in-text citations]

   References:
   [1] url
   [2] url
   ...
   </answer>

Remember to be helpful, polite, and informative while maintaining assertiveness, objectivity, and brevity in your response.
"""
                    ),
                    (
                        "human",
                        f"<question> {question} </question> \n\n <context> {context} </context>"
                    )
                ]

        case "query_expansion":
              None

def test_model(model, question):
    st.write(question)
    start = time.time()
    response = model.predict(question)
    end = time.time()
    with st.expander("Reasoning history"):
         st.write(response["reasoning_history"])
    with st.expander("Final Context"):
         context = response["final_answer"]["context"]
         st.write([context[s][i].page_content for s in context for i in range(len(context[s]))])
    st.write(response["final_answer"]["answer"])
    st.write(f"Time taken: {end-start}s")
    st.write("-----")

if st.button("Build model"):
    with st.echo():
        model = model_builder.RAG_model(
            structure_name=f"{structure}-{llm_type}",
            dbs_name=dbs, 
            embeddings_name = embedding_model, 
            chat_pars = chat_pars,
            retriever_pars = retriever_pars,
            prompt_template = prompt_template,
            final_prompt_template = final_prompt_template,
            reasoning_limit = reasoning_limit
        )

        test_model(model, "what is optimism?")
        #test_model(model, "who is Gonna?")
        test_model(model, "Are Governance Fund grant applications currently being processed?")
        #test_model(model, "How can I participate in voting on Optimism governance proposals?")
        test_model(model, "Can you give me an overview of the OP token distribution?")
        #test_model(model, "what about Diego's vote rationale for RF3?")
