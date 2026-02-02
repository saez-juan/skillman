# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Skillman es una CLI tool para gestionar Claude skills usando un sistema de dos niveles:

- **Repositorio global**: `~/.claude/skillman/skills` - Todas las skills disponibles del usuario
- **Skills del proyecto**: `./.claude/skills` - Skills activas en el proyecto actual (symlinks)

Cuando ejecutás `skillman ls` en un proyecto, muestra solo las skills de ese proyecto. Se pueden agregar skills del repositorio global a proyectos individuales usando symlinks, manteniendo las skills de cada proyecto aisladas.

## Development Commands

### Setup inicial
```bash
# Instalar dependencias
poetry install
```

### Comandos principales
```bash
# Listar skills del proyecto actual
poetry run skillman ls

# Listar skills del repositorio global
poetry run skillman ls --global

# Listar skills disponibles para agregar
poetry run skillman ls --available

# Agregar una skill al proyecto
poetry run skillman add <skill-name>

# Remover una skill del proyecto
poetry run skillman remove <skill-name>
```

### Testing
```bash
# Ejecutar todos los tests
poetry run pytest

# Ejecutar tests con verbose output
poetry run pytest -v

# Ejecutar un archivo específico
poetry run pytest tests/test_cli.py

# Ejecutar un test específico
poetry run pytest tests/test_cli.py::TestListCommand::test_ls_project_skills
```

### Instalación global (opcional)
```bash
# Instalar como comando global
pip install .

# Luego se puede usar directamente
skillman ls
```

### Compilar a binario
```bash
# Compilar usando PyInstaller
poetry run pyinstaller skillman.spec --noconfirm

# El binario queda en dist/skillman
./dist/skillman --version
./dist/skillman ls

# Instalar en el sistema (copiar a un directorio en PATH)
sudo cp dist/skillman /usr/local/bin/
```

El binario es standalone y no requiere Python instalado.

## Architecture

### Estructura del proyecto
```
src/skillman/
├── __init__.py
├── __main__.py     # Entry point para binario y python -m skillman
├── cli.py          # Comandos CLI (ls, add, remove)
├── config.py       # Manejo de configuración (config.toml)
└── skills.py       # Lógica de parsing y discovery de skills

skillman.spec       # PyInstaller spec file para compilar binario
```

### Flujo de ejecución

1. **cli.py** - Entry point usando Click
   - `skillman ls`: lista skills del proyecto (`./.claude/skills`)
   - `skillman ls --global`: lista skills del repo global (`~/.claude/skillman/skills`)
   - `skillman ls --available`: lista skills disponibles para agregar
   - `skillman add <skill>`: crea symlink de global a proyecto
   - `skillman remove <skill>`: elimina symlink del proyecto
   - Usa Rich para output con colores y formato

2. **config.py** - Configuration management
   - `DEFAULT_SKILLS_PATH`: path del repositorio global (`~/.claude/skillman/skills`)
   - `ensure_config_exists()`: crea config file con defaults si no existe
   - `load_config()`: lee configuración desde `~/.claude/skillman/config.toml`
   - `get_skills_paths()`: retorna lista de paths donde buscar skills globales

3. **skills.py** - Core logic
   - `SkillManager`: clase principal para descubrir y parsear skills
   - `get_skills()`: escanea un directorio y retorna lista de skills
   - `_parse_skill()`: parsea un skill individual desde su directorio
   - `_extract_description()`: extrae descripción del frontmatter YAML en SKILL.md

### Conceptos clave

**PROJECT_SKILLS_DIR**: `./.claude/skills` (relativo al directorio actual)
- Contiene symlinks a skills del repositorio global
- Se crea automáticamente cuando ejecutás `skillman add`
- Es específico de cada proyecto

**DEFAULT_SKILLS_PATH**: `~/.claude/skillman/skills`
- Repositorio global de todas tus skills
- Se crea automáticamente la primera vez
- Shared entre todos los proyectos

**Symlinks**:
- `skillman add` crea symlinks de global a proyecto
- `skillman remove` elimina solo el symlink, no la skill global
- Permite que múltiples proyectos usen la misma skill sin duplicación

### Configuración

El archivo de configuración se ubica en `~/.claude/skillman/config.toml` y se crea automáticamente la primera vez que se ejecuta skillman.

```toml
# Lista de paths donde buscar skills globales
skills_paths = [
    "/home/user/.claude/skillman/skills"
]
```

Por defecto, skillman busca skills globales en `~/.claude/skillman/skills`.

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
├── test_cli.py      # Tests de comandos CLI (ls, add, remove)
├── test_config.py   # Tests de configuración
├── test_skills.py   # Tests de SkillManager
└── fixtures/        # Skills de prueba con diferentes configuraciones
```

### Tests de CLI

Los tests de CLI usan `CliRunner` de Click y testean:
- `skillman ls` sin skills en proyecto (warning)
- `skillman ls --global` con skills globales
- `skillman ls --available` filtrando skills ya agregadas
- `skillman add <skill>` creando symlinks
- `skillman remove <skill>` eliminando symlinks
- Edge cases: skills que no existen, symlinks rotos, etc.

### Ejecutar tests
```bash
# Todos los tests
poetry run pytest

# Con verbose output
poetry run pytest -v

# Un archivo específico
poetry run pytest tests/test_cli.py

# Un test específico
poetry run pytest tests/test_cli.py::TestListCommand::test_ls_project_skills
```

## Dependencies

- **click** ^8.0.0 - CLI framework
- **rich** ^13.0.0 - Terminal UI con colores y tablas
- **tomli** ^2.0.0 - TOML parser (solo Python < 3.11)
- **tomli-w** ^1.0.0 - TOML writer
- **pytest** ^7.0.0 - Testing (dev dependency)
- **pyinstaller** ^6.0.0 - Build standalone binaries (dev dependency)

## Python version

- Requiere Python >= 3.8
- Usa Poetry para dependency management

## Convenciones del código

- Type hints en todas las funciones públicas
- Docstrings estilo Google para clases y métodos principales
- `Path` objects para file paths (no strings)
- Return `None` o listas vacías para casos sin resultados (no exceptions)
- Regex para parsing de frontmatter YAML (no parser externo)
- Symlinks para vincular skills (no copy-paste)
