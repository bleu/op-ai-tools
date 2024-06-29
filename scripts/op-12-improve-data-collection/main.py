# relevant to 002-dataset-governance-docs
import csv
import sys
import os

def get_folder_docs(link):
    None

def process_all_txt(repo_name, all_txt_file):
    # Read the content of all.txt
    with open(all_txt_file, "r") as file:
        lines = file.readlines()

    # Initialize variables
    data = []
    current_file = None
    current_content = []
    sensitive_info_prefix = "/Users/"

    # Process each line
    for line in lines:
        if line.startswith("==>") and line.endswith("<==\n"):
            # New file detected
            if current_file is not None:
                # Save previous file's content
                sanitized_path = current_file.replace(sensitive_info_prefix, "")
                data.append(
                    (
                        repo_name,
                        os.path.basename(current_file),
                        sanitized_path,
                        "".join(current_content),
                    )
                )

            # Reset current content
            current_content = []
            # Extract the file path
            current_file = line[4:-4].strip()
        else:
            # Accumulate content lines
            current_content.append(line)

    # Don't forget to save the last file's content
    if current_file is not None:
        sanitized_path = current_file.replace(sensitive_info_prefix, "")
        data.append(
            (
                repo_name,
                os.path.basename(current_file),
                sanitized_path,
                "".join(current_content),
            )
        )

    # Write to CSV
    with open("output.csv", "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["repo", "filename", "fullpath", "content"])
        csvwriter.writerows(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <repo_name> <all_txt_file>")
        sys.exit(1)

    repo_name = sys.argv[1]
    all_txt_file = sys.argv[2]

    process_all_txt(repo_name, all_txt_file)
