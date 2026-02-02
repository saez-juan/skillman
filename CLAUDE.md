# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Skillman es una CLI tool para gestionar Claude skills. Permite listar, inspeccionar y eventualmente manipular skills ubicadas en `~/.claude/skills` o en cualquier directorio customizado.

## Development Commands

### Setup inicial
```bash
# Instalar dependencias
poetry install
```

### Comandos comunes
```bash
# Ejecutar la CLI en desarrollo
poetry run skillman ls

# Listar skills con información detallada
poetry run skillman ls --detailed

# Listar skills desde un directorio custom
poetry run skillman ls --path ./skills
poetry run skillman ls --path /path/to/skills

# Ejecutar tests
poetry run pytest

# Ejecutar tests con verbose output
poetry run pytest -v
```

### Instalación global (opcional)
```bash
# Instalar como comando global
pip install .

# Luego se puede usar directamente
skillman ls
```

## Architecture

### Estructura del proyecto
```
src/skillman/
├── __init__.py
├── cli.py          # Punto de entrada CLI (Click framework)
├── config.py       # Manejo de configuración (config.toml)
└── skills.py       # Lógica de parsing y discovery de skills
```

### Flujo de ejecución

1. **cli.py** - Entry point usando Click
   - Define comandos CLI (actualmente solo `ls`)
   - Maneja opciones (`--path`, `--detailed`)
   - Delega lógica de skills a `SkillManager`
   - Usa Rich para output con colores y formato

2. **config.py** - Configuration management
   - Maneja el archivo de configuración `~/.claude/skillman/config.toml`
   - `get_skills_paths()`: retorna lista de paths donde buscar skills
   - `add_skills_path()`: agrega un nuevo path a la configuración
   - `remove_skills_path()`: elimina un path de la configuración
   - Crea el archivo con valores por defecto si no existe

3. **skills.py** - Core logic
   - `SkillManager`: clase principal para descubrir y parsear skills
   - `get_skills()`: escanea un directorio y retorna lista de skills
   - `_parse_skill()`: parsea un skill individual desde su directorio
   - `_extract_description()`: extrae descripción del frontmatter YAML en SKILL.md

### Configuración

El archivo de configuración se ubica en `~/.claude/skillman/config.toml` y se crea automáticamente la primera vez que se ejecuta skillman.

```toml
# Lista de paths donde buscar skills
skills_paths = [
    "/home/user/.claude/skillman/skills",
    "/path/to/other/skills"
]
```

Por defecto, skillman busca skills en `~/.claude/skillman/skills`. Se pueden agregar múltiples paths y skillman buscará skills en todos ellos.

### Formato de skills

Un skill válido debe:
- Ser un directorio dentro del skills directory
- Contener un archivo `SKILL.md`
- El `SKILL.md` puede tener frontmatter YAML con metadata:
  ```yaml
  ---
  name: skill-name
  description: Descripción corta del skill
  disable-model-invocation: false
  ---
  ```

Opcionalmente puede contener:
- `/scripts` - Scripts auxiliares
- `/examples` - Ejemplos de uso
- `/resources` - Recursos adicionales
- `/templates` - Templates de código

### Skills de ejemplo

El repo incluye dos skills de referencia en `/skills`:
- `result-pattern` - Documentación sobre Result pattern de @vainilla/result
- `setup-ssh` - Guía para configurar SSH keys para packages privados

Estos skills son ejemplos reales tomados de otro proyecto y sirven para testing.

## Testing

### Estructura de tests
```
tests/
├── test_cli.py      # Tests de comandos CLI usando CliRunner
├── test_config.py   # Tests de configuración
├── test_skills.py   # Tests de SkillManager
└── fixtures/        # Skills de prueba con diferentes configuraciones
```

### Ejecutar tests
```bash
# Todos los tests
poetry run pytest

# Con verbose output
poetry run pytest -v

# Un archivo específico
poetry run pytest tests/test_cli.py

# Un test específico
poetry run pytest tests/test_cli.py::TestListCommand::test_ls_with_valid_path
```

## Dependencies

- **click** ^8.0.0 - CLI framework
- **rich** ^13.0.0 - Terminal UI con colores y tablas
- **tomli** ^2.0.0 - TOML parser (solo Python < 3.11)
- **tomli-w** ^1.0.0 - TOML writer
- **pytest** ^7.0.0 - Testing (dev dependency)

## Python version

- Requiere Python >= 3.8
- Usa Poetry para dependency management

## Convenciones del código

- Type hints en todas las funciones públicas
- Docstrings estilo Google para clases y métodos principales
- `Path` objects para file paths (no strings)
- Return `None` o listas vacías para casos sin resultados (no exceptions)
- Regex para parsing de frontmatter YAML (no parser externo)
