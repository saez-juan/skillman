# Skillman

CLI tool to manage Claude skills with ease.

## Concept

Skillman manages Claude skills using a two-tier system:

- **Global repository**: `~/.claude/skillman/skills` - All your available skills
- **Project skills**: `./.claude/skills` - Skills active in the current project (symlinks)

When you run `skillman ls` in a project, it shows skills specific to that project. You can add skills from your global repository to individual projects using symlinks, keeping each project's skills isolated.

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

### List skills in current project

```bash
# Show skills in current project (./.claude/skills)
skillman ls

# Show all skills in global repository
skillman ls --global

# Show skills available to add (in global but not in project)
skillman ls --available
```

### Manage project skills

```bash
# Add a skill from global repository to current project
skillman add <skill-name>

# Remove a skill from current project
skillman remove <skill-name>
```

### Example workflow

```bash
# Check what skills are available globally
skillman ls --global

# Add a skill to your project
skillman add setup-ssh

# List skills in project
skillman ls

# Check what else you can add
skillman ls --available

# Remove a skill from project
skillman remove setup-ssh
```

## How it works

1. **Global skills** are stored in `~/.claude/skillman/skills`
2. When you run `skillman add <skill>`, it creates a **symlink** from `./.claude/skills/<skill>` to the global skill
3. `skillman ls` shows only the skills linked in your current project
4. Each project has its own set of skills, but they all reference the same global repository

This means:
- Skills are stored once (in global repository)
- Each project only references the skills it needs
- Updating a skill in the global repository updates it for all projects
- No duplication, easy management

## Features

- **Project-based skills**: Each project has its own set of skills
- **Global repository**: Centralized storage for all your skills
- **Symlink management**: Automatic symlink creation and removal
- **Beautiful output**: Rich terminal UI with colors
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
- **tomli** >= 2.0.0 - TOML parser (Python < 3.11)
- **tomli-w** >= 1.0.0 - TOML writer
- **pytest** >= 7.0.0 - Testing framework (dev dependency)
- **pyinstaller** >= 6.0.0 - Build standalone binaries (dev dependency)

## Project Structure

```
skillman/
├── src/
│   └── skillman/
│       ├── __init__.py
│       ├── __main__.py      # Entry point for binary
│       ├── cli.py           # Main CLI interface
│       ├── config.py        # Configuration management
│       └── skills.py        # Skills parsing logic
├── tests/                   # Unit tests
│   ├── test_cli.py          # CLI command tests
│   ├── test_config.py       # Config tests
│   ├── test_skills.py       # SkillManager tests
│   └── fixtures/            # Test fixtures
├── CLAUDE.md                # Guidance for Claude Code
├── pyproject.toml           # Poetry configuration
└── README.md
```

## License

MIT
