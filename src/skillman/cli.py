"""Main CLI interface for skillman."""

from pathlib import Path
import click
from rich.console import Console

from .config import get_skills_paths
from .skills import SkillManager

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="skillman")
def cli():
    """Skillman - Manage your Claude skills."""
    pass


@cli.command("ls")
@click.option(
    "--path",
    "-p",
    default=None,
    help="Custom path to skills directory (default: paths from config)",
)
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Show detailed information about each skill",
)
def list_skills(path, detailed):
    """List all available Claude skills."""

    # Determine the skills directories
    if path:
        skills_dirs = [Path(path)]
    else:
        skills_dirs = get_skills_paths()

    all_skills = []
    valid_dirs = []

    for skills_dir in skills_dirs:
        if not skills_dir.exists():
            console.print(f"Skills directory not found: {skills_dir}", style="yellow")
            continue

        valid_dirs.append(skills_dir)
        manager = SkillManager(skills_dir)
        skills = manager.get_skills()
        all_skills.extend(skills)

    if not valid_dirs:
        console.print("No valid skills directories found.", style="yellow")
        console.print("Tip: Create the directory or specify a custom path with --path", style="dim")
        return

    if not all_skills:
        console.print("No skills found in configured paths.", style="yellow")
        return

    # Display skills
    if detailed:
        _display_detailed_skills(all_skills, valid_dirs)
    else:
        _display_simple_skills(all_skills, valid_dirs)


def _display_simple_skills(skills, skills_dirs):
    """Display skills in a simple list format."""
    console.print(f"\nSkills ({len(skills)}):", style="bold")
    console.print()

    for skill in sorted(skills, key=lambda s: s["name"]):
        name = skill["name"]
        desc = skill["description"] or "No description"
        console.print(f"  {name}", style="cyan")
        console.print(f"    {desc}", style="dim")
        console.print()

    console.print("Locations:", style="dim")
    for d in skills_dirs:
        console.print(f"  - {d}", style="dim")


def _display_detailed_skills(skills, skills_dirs):
    """Display skills with detailed information."""
    console.print(f"\nSkills ({len(skills)}):", style="bold")
    console.print()

    for skill in sorted(skills, key=lambda s: s["name"]):
        console.print(f"  {skill['name']}", style="cyan bold")

        if skill["description"]:
            console.print(f"    {skill['description']}", style="white")
        else:
            console.print("    No description", style="dim")

        console.print(f"    Path: {skill['path']}", style="dim")

        extras = []
        if skill.get("has_scripts"):
            extras.append("scripts")
        if skill.get("has_examples"):
            extras.append("examples")
        if skill.get("has_resources"):
            extras.append("resources")

        if extras:
            console.print(f"    Contains: {', '.join(extras)}", style="dim")

        console.print()

    console.print("Locations:", style="dim")
    for d in skills_dirs:
        console.print(f"  - {d}", style="dim")


if __name__ == "__main__":
    cli()
