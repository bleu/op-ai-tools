from op_brains.chat.utils import process_question
from op_brains.config import CHAT_MODEL

import json
import time
import pandas as pd

time_related_dataset = pd.read_csv("datasets/time_related.csv")
time_related_test = time_related_dataset.question.tolist()
time_related_expected = time_related_dataset.expected.tolist()

from_fragments_dataset = pd.read_csv("datasets/fragmented_easy.csv")
from_fragments_test = from_fragments_dataset.question.tolist()
from_fragments_expected = from_fragments_dataset.answer.tolist()

tests = {
    "time_related": time_related_test,
    "from_fragments": from_fragments_test,
}

expected = {
    "time_related": time_related_expected,
    "from_fragments": from_fragments_expected,
}

models2test = [
    CHAT_MODEL
]


def batch_test():
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

        answers[m] = {}
        for test_type, test_queries in tests.items():
            answers[m][test_type] = {}
            for query in test_queries:
                start = time.time()
                out = process_question(query, [], verbose=True)
                print("----------")
                end = time.time()
                out["time_taken"] = end - start
                answers[m][test_type][query] = out

    json.dump(answers, open("test_results/answers.json", "w"), indent=4)
    json2csv(answers)


def json2csv(answers):
    for test_type, test_queries in tests.items():
        out_answers = []
        for query in test_queries:
            out_answers.append(
                {
                    "query": query,
                    "expected": expected[test_type][test_queries.index(query)],
                }
            )
            for m in models2test:
                answer = answers[m][test_type][query]
                out_answers[-1].update(
                    {
                        f"answer_{m}": answer["answer"],
                        f"time_taken_{m}": answer["time_taken"],
                        #f"reasoning_level_{m}": len(answer["reasoning"]),
                    }
                )
        pd.DataFrame(out_answers).to_csv(f"test_results/{test_type}.csv", index=False)

def single_test(query, desired_word):
    ok = 0
    for i in range(10):
        out = process_question(query, [], verbose=True)
        if desired_word in out["answer"]:
            ok += 1

    print(ok)
    

if __name__ == "__main__":
    batch_test()
    #single_test("who is the grants council lead?", "Gonna")
    #single_test("Who is the security council lead?", "Alisha")
    #single_test("What are some of the key metrics used to evaluate the performance of growth experiment programs?", "ETH")
    #single_test("Is the Law of Chains a legally binding contract?", "No")

