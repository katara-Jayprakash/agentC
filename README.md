# Claude Code

A small command-line coding assistant that can read files, write files, and run shell commands.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- An [OpenRouter](https://openrouter.ai/) API key

## Setup

Clone the repository and move into the project directory:

```sh
git clone <repository-url>
cd claude-code
```

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Install the dependencies:

```sh
uv sync
```

## Run

Pass your prompt using the `-p` option:

```sh
./your_program.sh -p "List the files in this directory"
```

You can also run the Python module directly:

```sh
uv run -m app.main -p "Read pyproject.toml"
```

The assistant can execute commands and modify files, so run it only in a directory where those actions are safe.
