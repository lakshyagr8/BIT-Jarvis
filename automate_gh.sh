#!/bin/bash

set -e
set -o pipefail

# git init .
# echo "initialized git repo"

# echo -e "\n"
# echo "Please provide repository name: "
# read repo_name

# echo "Do you want the repo to be Public or Private"
# read repo_status

# echo -e "\nCreating remote github repo......"
# gh repo create $repo_name --$repo_status
# echo "Successful, Github creation!"

# echo -e "\nWorking on remote URL....."
# URL=https://github.com/ragitu5552/"$repo_name".git
# git remote add origin "$URL"
# echo "Added remote URL"

# git branch -a

# echo -e "\nInstalling required Python packages"
# pip install groq

echo -e "\nLLM is processing each file"
cat <<'EOF' > script.py
import os
import glob
import groq

# Initialize Groq API (Replace 'your_api_key' with an actual key)
GROQ_API_KEY = "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"
client = groq.Client(api_key=GROQ_API_KEY)

def collect_python_files(directory=".", exclude_dirs=None, exclude_files=None):
    """
    Collects all Python (.py) files in the given directory (including subdirectories),
    but excludes specified subdirectories and files.

    Parameters:
        directory (str): The root directory to search.
        exclude_dirs (list): A list of subdirectory names to exclude.
        exclude_files (list): A list of filename patterns to exclude (e.g., "selection.py").

    Returns:
        dict: A dictionary where keys are filenames and values are their content.
    """
    if exclude_dirs is None:
        exclude_dirs = []
    if exclude_files is None:
        exclude_files = []

    py_files = glob.glob(os.path.join(directory, "**", "*.py"), recursive=True)
    collected_data = {}

    for file_path in py_files:
        # Check if the file path contains any of the excluded directories
        if any(excluded in file_path.split(os.sep) for excluded in exclude_dirs):
            continue

        # Check if the file name matches any of the excluded file patterns
        file_name = os.path.basename(file_path)
        if any(file_name == excluded for excluded in exclude_files):
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            collected_data[file_path] = file.read()

    return collected_data

def create_context_file(collected_data, output_file="context.txt"):
    """
    Writes the collected Python file contents into a single text file.
    """
    with open(output_file, "w", encoding="utf-8") as file:
        for filename, content in collected_data.items():
            file.write(f"### {filename}\n\n")
            file.write(content + "\n\n")

    print(f"Context file saved as: {output_file}")

def generate_markdown_with_groq(context_file="context.txt", output_md="generated.md"):
    """
    Feeds the context file to Groq API and generates a markdown file.
    """
    try:
        with open(context_file, "r", encoding="utf-8") as file:
            context = file.read()
    except FileNotFoundError:
        print(f"Error: Context file '{context_file}' not found.")
        return

    context = context[:8000]

    system_prompt = "You are an expert technical writer AI. Your task is to generate ONLY the raw markdown content for a GitHub README file based on the provided code context. Adhere strictly to the user's instructions."
    user_prompt = f"""Generate ONLY the raw markdown content for a professional, well-structured GitHub README.md file using the code context below.

**Key Instructions:**
1.  **Direct Markdown Output:** Start the response *immediately* with the markdown content (e.g., the H1 title `# Project Title`). Do NOT include *any* introductory text, conversational phrases (like "Here is...", "Sure, check this out..."), explanations, or summaries *before* the actual markdown begins.
2.  **Structure & Content:** Analyze the context to infer the project's purpose. Create logical sections like:
    * Project Title (H1 `#`)
    * Short Description/Tagline
    * ✨ Key Features (Bulleted list)
    * ⚙️ Installation (Use code blocks for commands)
    * 🚀 Usage (Provide clear examples, use code blocks)
    * 🤝 Contributing (Placeholder is okay)
    * 📄 License (Placeholder is okay)
    * *(Adapt sections based *only* on information inferable from the context)*
3.  **Formatting:** Use standard GitHub Flavored Markdown. Use emojis thoughtfully. Use code fences (e.g., ```python) for code examples.
4.  **Source:** Base all content strictly on the provided code context.

**Project Code Context:**
{context}
**(Remember: Output only the raw markdown content below this line. No introduction!)**"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        generated_text = response.choices[0].message.content

        with open(output_md, "w", encoding="utf-8") as file:
            file.write(generated_text)

        print(f"Markdown file saved as: {output_md}")

    except Exception as e:
        print(f"Error generating markdown: {e}")

# Actually call the functions
python_files = collect_python_files(directory=".", exclude_dirs=["myenv", "__pycache__", "vectorized_db", "vectorstore", "script.py"])
create_context_file(python_files)
generate_markdown_with_groq()
EOF

python script.py

# Copy the generated markdown to README.md
cat generated.md > README.md

cat generated.md
# Now we can remove the script
echo -e '\n\nRemoving during execution generated files'
#rm script.py
rm context.txt
rm generated.md
rm script.py
git add .
git commit -m "First commit"

echo "pushing to master..."
git push -u origin master
echo "pushed to master branch"


