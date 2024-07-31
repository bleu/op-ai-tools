from op_chat_brains.chat import model_utils, system_structure
from op_chat_brains.config import DB_STORAGE_PATH

import os, json, time
import pandas as pd

questions_index = "questions_index.json"
embedding_model = "text-embedding-ada-002"

easy_test = [
    #"What are the steps involved in becoming an Optimism Ambassador?",
    #"What is an Airdrop?",
    #"What is required for a non-grant proposal to move to a vote in the Optimism governance process?",
    #"What is required for a proposal to move to a vote in the Optimism governance process?",
    #"What is the purpose of the Code of Conduct Council?",
    #"When does Voting Cycle 22 begin and end?",
    "Are there any specific KYC requirements for grant recipients in the Optimism community?",
    "Can I refer to OP token grants in terms of their USD value?",
    "Can Optimism currently censor user transactions?",
    "Can projects that have already received a grant apply for more funding?",
    "Can the length of the challenge period be changed?",
    "Do I need to claim my tokens for Airdrop #2?",
    "Do I need to hold a minimum amount of tokens to submit a proposal?",
    "Does the Law of Chains create any formal relationships among participants?",
    "How are Mission Requests ranked and funded in the Optimism Governance system?",
    "How are the rubrics for reviewing Mission applications in Season 5 structured?",
    "How can I become a support NERD in the Optimism community?",
    "How can I find out who my current delegate is and see their voting record?",
    "How can I get involved in the Optimism Collective?",
    "How can I get test tokens on the OP Goerli network?",
    "How can I get testnet ETH to deploy a smart contract on OP Sepolia?",
    "How can I participate in Optimism's Demo Day?",
    "How can I participate in Token House governance without a significant time commitment?",
    "How can I report a bug or suggest a feature for the Optimism SDK?",
    "How can I start the process of becoming an Optimism Ambassador?",
    "How does Optimism ensure that its protocol remains sustainable?",
    "How does Optimism's bi-cameral governance system help prevent plutocratic governance?",
    "How does Retro Funding 4 plan to reward the use of Open Source licenses?",
    "How does funding public goods drive demand for blockspace in the Optimism ecosystem?",
    "How does one progress through the ambassador roles in Optimism Governance?",
    "How does the Citizens' House contribute to the governance of the Optimism Collective?",
    "How does the Impact Evaluation Framework assist badgeholders in reviewing RetroPGF applications?",
    "How does the OP Passport project enhance privacy and security for governance participants?",
    "How does the Optimism Collective generate value for its ecosystem?",
    "How does the Optimism Collective plan to align the community in Season 4?",
    "How does the Optimism Collective plan to fund public goods?",
    "How does the Optimism Collective plan to handle identity and reputation?",
    "How does the Pairwise voting system work in the context of RetroPGF?",
    "How does the voting schedule work in Optimism's Token House governance?",
    "How is Citizenship in the Citizens' House expected to evolve over time?",
    "How is the scope and voting process for Retro Funding determined?",
    "How long do I need to offer support before becoming a `support-NERD`?",
    "How many OP tokens were involved in the private token sale in March 2024?",
    "How much funding was allocated in the first round of Retroactive Public Goods Funding by the Optimism Collective?",
    "How should badgeholders measure the Council’s impact?",
    "How were the badgeholders for RetroPGF Round 2 selected?",
    "Is the Law of Chains a legally binding contract?",
    "Is there a beginner-friendly version of the TechNERD training?",
    "What actions can lead to losing my NERD status?",
    "What actions can lead to losing your Ambassador status?",
    "What are Retroactive Public Goods Funding (RetroPGF) rounds?",
    "What are some community concerns regarding the enforcement of the Code of Conduct?",
    "What are some concerns related to the cost of on-chain voting?",
    "What are some examples of projects that can be nominated for the Tooling & Utilities category?",
    "What are some of the key features and improvements that have been added to Agora based on user feedback?",
    "What are some of the key metrics used to evaluate the performance of growth experiment programs?",
    "Are Governance Fund grant applications currently being processed?",
    "Can I create NFTs on the OP Mainnet without knowing how to code?",
    "How are protocols selected for the Protocol Delegation Program?",
    "How can DAOs incentivize more thoughtful participation in governance votes?",
    "How can I contribute to translating Optimism's User Docs?",
    "How can I get involved in running local events for the Optimism community?",
    "How can I participate in general governance discussions for Optimism?",
    "How can I promote my project once it's deployed on the Superchain?",
    "How can limiting delegate voting power promote decentralization and new delegate inclusion?delegate",
    "How do I apply for a Mission Grant on Optimism?",
    "How do Missions relate to Retro Funding?",
    "How does a non-grant proposal proceed to a vote in the Optimism Governance Forum?",
    "How does the Delta network upgrade propose to reduce L1 costs for OP Chains?",
    "How does the Grants Council ensure the responsible allocation of funds?",
    "How does the Optimism Collective support builders with grants?",
    "How does the bicameral governance system of the Optimism Token House limit the influence of large token holders?",
    "How has the votable supply of OP tokens changed during Season 3?",
    "How many project grants were approved and how many were rejected in the first three voting cycles?",
    "Is there any reward for translating documents for Optimism?",
    "What accountability measures are in place for teams receiving grants from the Governance Fund?",
]

tests = {
    "easy": easy_test,
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

    index_retriever = model_utils.RetrieverBuilder.build_index(
        embedding_model,
        k_max=2,
        treshold=0.9
        )
    
    default_retriever = model_utils.RetrieverBuilder.build_faiss_retriever(
        dbs, 
        embedding_model,
        k = 5,
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
            }
        )

        system = system_structure.RAG_system(
            REASONING_LIMIT = 2,
            models_to_use = [chat_model, chat_model],
            factual_retriever = default_retriever,
            temporal_retriever = default_retriever,
            index_retriever = index_retriever,
            context_filter = model_utils.ContextHandling.filter,
            system_prompt_preprocessor = model_utils.Prompt.preprocessor,
            system_prompt_responder = model_utils.Prompt.responder,
            system_prompt_final_responder = model_utils.Prompt.final_responder
        )
        
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
        for m in models2test:
            for query in test_queries:
                answer = answers[m][test_type][query]
                out_answers.append({
                    "model": m,
                    "query": query,
                    "answer": answer["answer"],
                    "time_taken": answer["time_taken"],
                    "reasoning_level": len(answer["reasoning"])
                })
        pd.DataFrame(out_answers).to_csv(f"test_results/{test_type}.csv", index=False)


if __name__ == "__main__":
    main()
