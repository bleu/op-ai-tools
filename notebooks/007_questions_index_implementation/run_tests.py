import system_structure, model_utils
import os, json, time
import pandas as pd

questions_index = "questions_index.json"
embedding_model = "text-embedding-ada-002"


old_test = [
    "Are Governance Fund grant applications currently being processed?",
    "Who is the Grants Council Lead?",
    "Who is Gonna?",
    "What is optimism?",
    "what about Diego's vote rationale for RF3?",
]

easy_test = [
    "What are the steps involved in becoming an Optimism Ambassador?",
    "What is an Airdrop?",
    "What is required for a non-grant proposal to move to a vote in the Optimism governance process?",
    "What is required for a proposal to move to a vote in the Optimism governance process?",
    "What is the purpose of the Code of Conduct Council?",
    "When does Voting Cycle 22 begin and end?",
]

hard_test = [
    "How can I participate in voting on Optimism governance proposals?",
    "How many project grants were approved and how many were rejected in the last three voting cycles?",
    "Can you explain the most recent Optimism governance proposal?",
    "Can you give me an overview of the OP token distribution?",
    "What cycle is the current voting cycle?",
]

tests = {"old": old_test, "easy": easy_test, "hard": hard_test}

models2test = [
    "gpt-4o-mini",
]


def main():
    list_dbs = os.listdir("dbs")
    list_dbs = [db[:-3] for db in list_dbs if db[-3:] == "_db"]
    filter_out_dbs = ["summary_archived___old_missions"]
    dbs = [db for db in list_dbs if db not in filter_out_dbs]

    index_retriever = model_utils.build_index(questions_index, embedding_model)

    default_retriever = model_utils.build_retriever(
        dbs,
        embedding_model,
        k=20,
    )

    answers = {}
    for m in models2test:
        chat_model = (
            m,
            {
                "temperature": 0.0,
                "max_retries": 5,
                "max_tokens": 1024,
                "timeout": 60,
            },
        )

        system = system_structure.RAG_system(
            REASONING_LIMIT=1,
            models_to_use=[chat_model, chat_model],
            factual_retriever=default_retriever,
            temporal_retriever=default_retriever,
            index_retriever=index_retriever,
            context_filter=model_utils.ContextHandling.filter,
            system_prompt_preprocessor=model_utils.Prompt.preprocessor,
            system_prompt_responder=model_utils.Prompt.responder,
            system_prompt_final_responder=model_utils.Prompt.final_responder,
        )

        answers[m] = {}
        for test_type, test_queries in tests.items():
            answers[m][test_type] = {}
            for query in test_queries:
                start = time.time()
                out = system.predict(query, True)
                end = time.time()
                out["time_taken"] = end - start
                answers[m][test_type][query] = out

    json.dump(answers, open("test_results/answers.json", "w"), indent=4)

    json2csv(answers)


def json2csv(answers):
    for test_type, test_queries in tests.items():
        out_answers = []
        for m in models2test:
            for query in test_queries:
                answer = answers[m][test_type][query]
                out_answers.append(
                    {
                        "model": m,
                        "query": query,
                        "answer": answer["answer"],
                        "time_taken": answer["time_taken"],
                        "reasoning_level": len(answer["reasoning"]),
                    }
                )
        pd.DataFrame(out_answers).to_csv(f"test_results/{test_type}.csv", index=False)


if __name__ == "__main__":
    main()
