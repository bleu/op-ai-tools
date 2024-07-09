# op_chat_brains

op_chat_brains is an advanced question-answering system that utilizes Retrieval-Augmented Generation (RAG) techniques to provide intelligent responses tailored to specific domains. Designed for flexibility, it can be adapted for various use cases, such as Optimism Collective/Optimism L2 or ClickFiscal.

## Features

- **Multiple RAG Models**: Includes SimpleOpenAI, SimpleClaude, and ExpanderClaude.
- **Flexible Document Processing**: Handles various data sources.
- **API Endpoints**: Offers predictions and streaming responses.
- **CLI Interface**: Enables quick testing.
- **Structured Logging**: Tracks queries and responses.
- **Configurable Settings**: Easy customization through configuration.

## Project Structure

```
op_chat_brains/
├── api.py
├── cli.py
├── config.py
├── documents/
│   ├── __init__.py
│   ├── click.py
│   └── optimism.py
├── exceptions.py
├── model.py
├── prompts.py
├── setup.py
├── structured_logger.py
└── utils.py
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bleu/op-ai-tools.git
   cd pkg/op-chat-brains
   ```

2. Install dependencies:

   ```bash
   poetry install
   ```

## Usage

### Setup

Run the setup script to prepare the document databases:

```bash
python -m op_chat_brains.setup
```

### API

Start the Flask API:

```bash
python -m op_chat_brains.api
```

The API will be available at `http://localhost:3123` by default.

### CLI

Use the CLI for quick testing:

```bash
python -m op_chat_brains.cli "Your question here"
```

## Development

### Adding New Document Types

1. Create a new processing strategy in `documents/your_strategy.py`.
2. Implement the `DocumentProcessingStrategy` interface.
3. Add the new strategy to the appropriate `DocumentProcessorFactory`.

### Modifying RAG Models

Adjust the RAG models in `model.py` to add new functionalities or modify existing ones.

### Customizing Prompts

Edit the prompt templates in `prompts.py` to tailor the system's responses to your specific use case.

## Testing

Run the test suite using pytest:

```bash
pytest
```
