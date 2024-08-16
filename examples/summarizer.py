from op_brains.summarizer import summarize_thread

if __name__ == "__main__":
    urls = [
        "https://gov.optimism.io/t/special-voting-cycle-9a-grants-council/4198",
        "https://gov.optimism.io/t/airdrop-1-feedback-thread/80",
        "https://gov.optimism.io/t/retro-funding-4-onchain-builders-round-details/7988",
        "https://gov.optimism.io/t/the-future-of-optimism-governance/6471",
        "https://gov.optimism.io/t/optimism-community-call-recaps-recordings-thread/6937",
        "https://gov.optimism.io/t/how-to-start-a-project-at-optimism/7220",
        "https://gov.optimism.io/t/grant-misuse-reporting-process/7346",
        "https://gov.optimism.io/t/how-to-stay-up-to-date/6124",
    ]
    model_name = "gpt-4o"
    for url in urls:
        out = summarize_thread(url, model_name)
        for key, value in out.items():
            print(f"{key}: {value}")
        print("-------")
