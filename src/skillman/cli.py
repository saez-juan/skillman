"""Main CLI interface for skillman."""

import os
from pathlib import Path
import click
from rich.console import Console

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
    help="Custom path to skills directory (default: ~/.claude/skills)",
)
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Show detailed information about each skill",
)
def list_skills(path, detailed):
    """List all available Claude skills."""
    
    # Determine the skills directory
    if path:
        skills_dir = Path(path)
    else:
        skills_dir = Path.home() / ".claude" / "skills"
    
    # Check if directory exists
    if not skills_dir.exists():
        console.print(f"Skills directory not found: {skills_dir}", style="yellow")
        console.print("Tip: Create the directory or specify a custom path with --path", style="dim")
        return
    
    # Get skills using SkillManager
    manager = SkillManager(skills_dir)
    skills = manager.get_skills()
    
    if not skills:
        console.print(f"No skills found in: {skills_dir}", style="yellow")
        return
    
    # Display skills
    if detailed:
        _display_detailed_skills(skills, skills_dir)
    else:
        _display_simple_skills(skills, skills_dir)


def _display_simple_skills(skills, skills_dir):
    """Display skills in a simple list format."""
    console.print(f"\nSkills ({len(skills)}):", style="bold")
    console.print()
    
    for skill in sorted(skills, key=lambda s: s["name"]):
        name = skill["name"]
        desc = skill["description"] or "No description"
        console.print(f"  {name}", style="cyan")
        console.print(f"    {desc}", style="dim")
        console.print()
    
    console.print(f"Location: {skills_dir}", style="dim")


def _display_detailed_skills(skills, skills_dir):
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
    
    console.print(f"Location: {skills_dir}", style="dim")


if __name__ == "__main__":
    cli()
