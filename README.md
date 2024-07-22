# op-ai-tools

## Project Overview

Op Chat Brains is an advanced question-answering system designed to provide intelligent responses about Optimism using Retrieval-Augmented Generation (RAG) techniques. The project aims to create a complete AI solution that empowers users to access reliable information about Optimism through various interfaces.

## Key Features

Chatbot Web Application: Users can interact with the trained model and ask questions.
Automated Summary Reports: Summarizes forum discussions within the Optimism ecosystem.
Reporting Tool: Tracks user engagement and evaluates the model's effectiveness.

## Key Directories and Files

- `data/`: Contains raw and processed datasets.
- `notebooks/`: Jupyter notebooks for experimentation and analysis.
- `pkg/`: Core package containing the main application logic and modules.
- `scripts/`: Scripts for creating and improving datasets and conducting tests.
- `www/`: Frontend-related files, configurations, and dependencies.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry
- Node.js 20+
- Yarn

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bleu/op-ai-tools.git
   cd op-ai-tools
   ```

2. Set up the Python environment:

   ```bash
   cd pkg/op-chat-brains
   poetry install
   ```

3. Set up the web application:

   ```bash
   cd www
   yarn install
   ```

### Usage

#### Data Preparation

Run the data collection scripts:

```bash
python scripts/op-2-create-initial-documentation-dataset/main.py
python scripts/op-9-create-optimism-forum-dataset/main.py
```

Process the collected data:

```bash
cd pkg/op-chat-brains && python op_chat_brains/setup.py
```

#### Running the API

Start the Flask API:

```bash
cd pkg/op-chat-brains && python op_chat_brains/api.py
```

#### Running the Web Application

Start the Next.js development server:

```bash
cd www
yarn dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser to interact with the chat interface.

## Contact

For any questions or issues, please open an issue on GitHub or contact the project maintainers.
