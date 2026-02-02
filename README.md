# Skillman

CLI tool to manage Claude skills with ease.

## Installation

### Using Poetry (Recommended)

```bash
# Install dependencies
poetry install

# Run the CLI
poetry run skillman ls
```

### Using pip

```bash
# Install from source
pip install .
```

## Usage

### List skills

```bash
# List all skills in ~/.claude/skills
poetry run skillman ls

# Or if installed globally with pip
skillman ls

# List skills with detailed information
skillman ls --detailed

# List skills from a custom directory
skillman ls --path /path/to/skills
skillman ls --path ./skills  # relative path works too
```

### Examples

```bash
# Simple list
poetry run skillman ls

# Detailed view with descriptions and metadata
poetry run skillman ls --detailed

# Check skills in a specific directory
poetry run skillman ls --path ~/.claude/skills
```

## Features

- **List skills**: View all available Claude skills
- **Beautiful output**: Rich terminal UI with colors and tables
- **Detailed view**: See skill descriptions and additional resources
- **Flexible paths**: Support for custom skill directories
- **Fast**: Quick scanning and parsing of skill directories

## Development

```bash
# Install dependencies
poetry install

# Run the CLI in development
poetry run skillman ls

# Run tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v
```

## Requirements

- Python >= 3.8
- Poetry (for dependency management)

## Dependencies

- **click** >= 8.0.0 - CLI framework
- **rich** >= 13.0.0 - Beautiful terminal output
- **pytest** >= 7.0.0 - Testing framework (dev dependency)

## Project Structure

```
skillman/
├── src/
│   └── skillman/
│       ├── __init__.py
│       ├── cli.py          # Main CLI interface
│       └── skills.py       # Skills management logic
├── tests/                  # Unit tests
│   ├── test_cli.py         # CLI command tests
│   ├── test_skills.py      # SkillManager tests
│   └── fixtures/           # Test fixtures
├── skills/                 # Example skills for testing
│   ├── result-pattern/
│   └── setup-ssh/
├── CLAUDE.md               # Guidance for Claude Code
├── pyproject.toml          # Poetry configuration
└── README.md
```

## License

MIT
