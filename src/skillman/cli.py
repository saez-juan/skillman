"""Main CLI interface for skillman."""

import os
from pathlib import Path
import click
from rich.console import Console

from .config import DEFAULT_SKILLS_PATH
from .skills import SkillManager

console = Console()


def complete_global_skills(ctx, param, incomplete):
    """Shell completion for global skills (used by add command)."""
    if not DEFAULT_SKILLS_PATH.exists():
        return []

    manager = SkillManager(DEFAULT_SKILLS_PATH)
    skills = manager.get_skills()

    # Filter by incomplete prefix
    return [s["name"] for s in skills if s["name"].startswith(incomplete)]


def complete_project_skills(ctx, param, incomplete):
    """Shell completion for project skills (used by remove command)."""
    project_dir = get_project_skills_dir()
    if not project_dir.exists():
        return []

    manager = SkillManager(project_dir)
    skills = manager.get_skills()

    # Filter by incomplete prefix
    return [s["name"] for s in skills if s["name"].startswith(incomplete)]


def get_project_skills_dir():
    """Get project skills directory (relative to current working directory)."""
    return Path.cwd() / ".claude" / "skills"


@click.group()
@click.version_option(version="0.1.0", prog_name="skillman")
def cli():
    """Skillman - Manage your Claude skills."""
    pass


@cli.command("ls")
@click.option(
    "--global",
    "show_global",
    is_flag=True,
    help="Show skills from global repository (~/.claude/skillman/skills)",
)
@click.option(
    "--available",
    "show_available",
    is_flag=True,
    help="Show skills available to add (not yet in project)",
)
def list_skills(show_global, show_available):
    """List Claude skills in current project."""

    if show_global:
        _list_global_skills()
    elif show_available:
        _list_available_skills()
    else:
        _list_project_skills()


def _list_project_skills():
    """List skills in the current project."""
    if not get_project_skills_dir().exists():
        console.print("No skills in this project.", style="yellow")
        console.print(f"Tip: Use 'skillman add <skill-name>' to add skills from global repository", style="dim")
        return

    manager = SkillManager(get_project_skills_dir())
    skills = manager.get_skills()

    if not skills:
        console.print("No skills in this project.", style="yellow")
        console.print(f"Tip: Use 'skillman add <skill-name>' to add skills", style="dim")
        return

    _display_skills(skills, f"Project skills ({len(skills)}):")


def _list_global_skills():
    """List all skills in global repository."""
    if not DEFAULT_SKILLS_PATH.exists():
        console.print(f"Global skills directory not found: {DEFAULT_SKILLS_PATH}", style="yellow")
        console.print("Tip: Create the directory and add skills to it", style="dim")
        return

    manager = SkillManager(DEFAULT_SKILLS_PATH)
    skills = manager.get_skills()

    if not skills:
        console.print("No skills in global repository.", style="yellow")
        return

    _display_skills(skills, f"Global skills ({len(skills)}):")


def _list_available_skills():
    """List skills that can be added to the project (in global but not in project)."""
    if not DEFAULT_SKILLS_PATH.exists():
        console.print(f"Global skills directory not found: {DEFAULT_SKILLS_PATH}", style="yellow")
        return

    # Get global skills
    global_manager = SkillManager(DEFAULT_SKILLS_PATH)
    global_skills = global_manager.get_skills()

    if not global_skills:
        console.print("No skills in global repository.", style="yellow")
        return

    # Get project skills (if they exist)
    project_skill_names = set()
    if get_project_skills_dir().exists():
        project_manager = SkillManager(get_project_skills_dir())
        project_skills = project_manager.get_skills()
        project_skill_names = {s["name"] for s in project_skills}

    # Filter available skills (not in project)
    available_skills = [s for s in global_skills if s["name"] not in project_skill_names]

    if not available_skills:
        console.print("No skills available to add (all global skills are already in project).", style="yellow")
        return

    _display_skills(available_skills, f"Available skills ({len(available_skills)}):")


def _display_skills(skills, title):
    """Display skills in a simple list format."""
    console.print(f"\n{title}", style="bold")
    console.print()

    for skill in sorted(skills, key=lambda s: s["name"]):
        name = skill["name"]
        desc = skill["description"] or "No description"
        console.print(f"  {name}", style="cyan")
        console.print(f"    {desc}", style="dim")
        console.print()


@cli.command("add")
@click.argument("skill_name", shell_complete=complete_global_skills)
def add_skill(skill_name):
    """Add a skill from global repository to current project."""

    # Check if global skill exists
    global_skill_path = DEFAULT_SKILLS_PATH / skill_name
    if not global_skill_path.exists():
        console.print(f"Skill '{skill_name}' not found in global repository.", style="red")
        console.print(f"Location: {DEFAULT_SKILLS_PATH}", style="dim")
        return

    # Verify it's a valid skill (has SKILL.md)
    if not (global_skill_path / "SKILL.md").exists():
        console.print(f"'{skill_name}' is not a valid skill (missing SKILL.md).", style="red")
        return

    # Create project skills directory if it doesn't exist
    get_project_skills_dir().mkdir(parents=True, exist_ok=True)

    # Check if skill already exists in project
    project_skill_path = get_project_skills_dir() / skill_name
    if project_skill_path.exists():
        console.print(f"Skill '{skill_name}' already exists in project.", style="yellow")
        return

    # Create symlink
    try:
        os.symlink(global_skill_path, project_skill_path, target_is_directory=True)
        console.print(f"Added skill '{skill_name}' to project.", style="green")
    except Exception as e:
        console.print(f"Failed to add skill: {e}", style="red")


@cli.command("remove")
@click.argument("skill_name", shell_complete=complete_project_skills)
def remove_skill(skill_name):
    """Remove a skill from current project."""

    project_skill_path = get_project_skills_dir() / skill_name

    # Check if skill exists in project
    if not project_skill_path.exists():
        console.print(f"Skill '{skill_name}' not found in project.", style="yellow")
        return

    # Remove symlink
    try:
        if project_skill_path.is_symlink():
            project_skill_path.unlink()
            console.print(f"Removed skill '{skill_name}' from project.", style="green")
        else:
            console.print(f"Warning: '{skill_name}' is not a symlink. Use regular file operations to remove it.", style="yellow")
    except Exception as e:
        console.print(f"Failed to remove skill: {e}", style="red")


@cli.command("completion")
@click.option(
    "--shell",
    type=click.Choice(["bash", "zsh", "fish"]),
    default="bash",
    help="Shell type (default: bash)",
)
@click.option(
    "--install",
    is_flag=True,
    help="Install completion script automatically",
)
def completion(shell, install):
    """Generate shell completion script."""

    if shell == "bash":
        script_name = "skillman-complete.bash"
        install_path = Path.home() / ".local" / "share" / "bash-completion" / "completions" / "skillman"

        if install:
            # Generate and install
            import subprocess
            import sys
            import shutil

            try:
                # Try to find the skillman command in PATH
                skillman_cmd = shutil.which("skillman")

                if not skillman_cmd:
                    # Fallback: use poetry run if available
                    if shutil.which("poetry"):
                        cmd = ["poetry", "run", "skillman"]
                    else:
                        console.print("Could not find 'skillman' command.", style="red")
                        console.print("\nInstall skillman first, then run:", style="dim")
                        console.print("  skillman completion --install", style="cyan")
                        return
                else:
                    cmd = [skillman_cmd]

                # Generate completion script
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    env={**os.environ, "_SKILLMAN_COMPLETE": "bash_source"}
                )

                if result.returncode != 0 or not result.stdout.strip():
                    console.print("Failed to generate completion script.", style="red")
                    console.print("\nManual installation:", style="dim")
                    console.print("  eval \"$(_SKILLMAN_COMPLETE=bash_source skillman)\"", style="cyan")
                    return

                # Create directory if needed
                install_path.parent.mkdir(parents=True, exist_ok=True)

                # Write completion script
                install_path.write_text(result.stdout)

                console.print(f"Bash completion installed to: {install_path}", style="green")
                console.print("\nTo activate, add this to your ~/.bashrc:", style="dim")
                console.print(f"  source {install_path}", style="cyan")
                console.print("\nOr restart your shell.", style="dim")

            except Exception as e:
                console.print(f"Failed to install completion: {e}", style="red")
                console.print("\nManual installation:", style="dim")
                console.print("  eval \"$(_SKILLMAN_COMPLETE=bash_source skillman)\"", style="cyan")
        else:
            # Just show instructions
            console.print("To enable bash completion, add this to your ~/.bashrc:", style="bold")
            console.print()
            console.print("  eval \"$(_SKILLMAN_COMPLETE=bash_source skillman)\"", style="cyan")
            console.print()
            console.print("Or install it permanently:", style="dim")
            console.print("  skillman completion --install", style="cyan")

    elif shell == "zsh":
        console.print("To enable zsh completion, add this to your ~/.zshrc:", style="bold")
        console.print()
        console.print("  eval \"$(_SKILLMAN_COMPLETE=zsh_source skillman)\"", style="cyan")
        console.print()

    elif shell == "fish":
        console.print("To enable fish completion, add this to your config:", style="bold")
        console.print()
        console.print("  eval (env _SKILLMAN_COMPLETE=fish_source skillman)", style="cyan")
        console.print()


if __name__ == "__main__":
    cli()
