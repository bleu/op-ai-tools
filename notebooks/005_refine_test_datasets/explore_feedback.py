import pandas as pd

"# Explore the feedback in the test dataset"

"## Load the data"
df = pd.read_csv("dataset_test_with_feedback.csv")
df
# columns: ['question', 'is the question relevant? (0/1)', 'answer', 'is the answer right? (0/1)', 'corrections to the answer', 'notes', 'origin']

"## irrelevant questions:"
irrelevant_questions = df[df["is the question relevant? (0/1)"] == 0]
irrelevant_questions

"## relevant questions:"
relevant_questions = df[df["is the question relevant? (0/1)"] == 1]
relevant_questions

"### relevant questions with non-problematic answers:"
# select if there is no note or correction
relevant_questions_without_problems = relevant_questions[
    relevant_questions["corrections to the answer"].isnull()
    & relevant_questions["notes"].isnull()
]
relevant_questions_without_problems = relevant_questions_without_problems.drop(
    columns=[
        "is the question relevant? (0/1)",
        "is the answer right? (0/1)",
        "corrections to the answer",
        "notes",
    ]
)
relevant_questions_without_problems

relevant_questions_without_problems.to_csv("easy_test_dataset.csv", index=False)


"### relevant questions with problematic answers:"
# select if there is note or correction
relevant_questions_with_problems = relevant_questions[
    relevant_questions["corrections to the answer"].notnull()
    | relevant_questions["notes"].notnull()
]
relevant_questions_with_problems = relevant_questions_with_problems.drop(
    columns=["is the question relevant? (0/1)", "is the answer right? (0/1)"]
)
relevant_questions_with_problems

relevant_questions_with_problems.to_csv("hard_test_dataset.csv", index=False)
