from op_chat_brains.chat import model_utils, system_structure
from op_chat_brains.config import DB_STORAGE_PATH

import os, json, time
import pandas as pd

questions_index = "index/questions.json"

time_related_dataset = pd.read_csv("datasets/time_related.csv")
time_related_test = time_related_dataset.question.tolist()
time_related_expected = time_related_dataset.expected.tolist()

tests = {
    "time_related": time_related_test,
}

expected = {
    "time_related": time_related_expected,
}

models2test = [
    "gpt-4o-mini",
    "claude-3-sonnet-20240229",
]


def main():
    list_dbs = os.listdir(DB_STORAGE_PATH)
    list_dbs = [db[:-3] for db in list_dbs if db[-3:] == "_db"]
    filter_out_dbs = ['summary_archived___old_missions']
    dbs = [db for db in list_dbs if db not in filter_out_dbs]

    questions_index_retriever = model_utils.RetrieverBuilder.build_questions_index(
        k_max=2,
        treshold=0.9
    )
    
    keywords_index_retriever = model_utils.RetrieverBuilder.build_keywords_index(
        k_max=5,
        treshold=0.93
    )

    default_retriever = model_utils.RetrieverBuilder.build_faiss_retriever(
        dbs, 
        k = 5,
    )

    def retriever(query : str, info_type : str, reasoning_level : int) -> list:
        if reasoning_level == 0:
            context = keywords_index_retriever(query)
            if len(context) > 0:
                return context
            
        if reasoning_level < 2:
            context = questions_index_retriever(query)
            if len(context) > 0:
                return context
        
        return default_retriever(query)

    answers = {}
    for m in models2test:
        chat_model = (
            m,
            {
                "temperature": 0.0,
                "max_retries": 5,
                "max_tokens": 1024,
                "timeout": 60,
            }
        )

        system = system_structure.RAG_system(
            REASONING_LIMIT = 2,
            models_to_use = [chat_model, chat_model],
            retriever = retriever,
            context_filter = model_utils.ContextHandling.filter,
            system_prompt_preprocessor = model_utils.Prompt.preprocessor,
            system_prompt_responder = model_utils.Prompt.responder,
            system_prompt_final_responder = model_utils.Prompt.final_responder
        )

        query = "when airdrop 3 took place?"
        context = keywords_index_retriever(query, "airdrop 3")
        result, is_enough = system.responder_LLM(query, context, "", "", final = False)
        print(result)

        query = "when airdrop 4 took place?"
        context = keywords_index_retriever(query, "airdrop 4")
        result, is_enough = system.responder_LLM(query, context, "", "", final = False)
        print(result)

        
        answers[m] = {}
        for test_type, test_queries in tests.items():
            answers[m][test_type] = {}
            for query in test_queries:
                start = time.time()
                out = system.predict(query, [], True)
                end = time.time()
                out["time_taken"] = end - start
                answers[m][test_type][query] = out

    json.dump(answers, open("test_results/answers.json", "w"), indent=4)
    json2csv(answers)
 

def json2csv(answers):
    for test_type, test_queries in tests.items():
        out_answers = []
        for query in test_queries:
            out_answers.append({
                "query": query,
                "expected": expected[test_type][test_queries.index(query)]
            })
            for m in models2test:
                answer = answers[m][test_type][query]
                out_answers[-1].update({
                    f"answer_{m}": answer["answer"],
                    f"time_taken_{m}": answer["time_taken"],
                    f"reasoning_level_{m}": len(answer["reasoning"])
                })
        pd.DataFrame(out_answers).to_csv(f"test_results/{test_type}.csv", index=False)


if __name__ == "__main__":
    main()
