"""Tests for cli.py - CLI commands."""

import os
from pathlib import Path
import pytest
from click.testing import CliRunner
from unittest.mock import patch

from skillman.cli import cli


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_global_skills(tmp_path):
    """Create mock global skills directory."""
    global_dir = tmp_path / "global"
    global_dir.mkdir()

    # Create skill-1
    skill1 = global_dir / "skill-1"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text(
        "---\nname: skill-1\ndescription: First skill\n---\n# Skill 1"
    )

    # Create skill-2
    skill2 = global_dir / "skill-2"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text(
        "---\nname: skill-2\ndescription: Second skill\n---\n# Skill 2"
    )

    return global_dir


@pytest.fixture
def mock_project_dir(tmp_path):
    """Create mock project directory."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    return project_dir


class TestListCommand:
    """Tests for 'skillman ls' command."""

    def test_ls_no_project_skills(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show warning when no skills in project."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        assert "No skills in this project" in result.output

    def test_ls_with_project_skills(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should list skills in project."""
        monkeypatch.chdir(mock_project_dir)

        # Create project skills directory with a symlink
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)

        skill1_link = project_skills / "skill-1"
        os.symlink(mock_global_skills / "skill-1", skill1_link, target_is_directory=True)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls"])

        assert result.exit_code == 0
        assert "Project skills (1)" in result.output
        assert "skill-1" in result.output
        assert "First skill" in result.output

    def test_ls_global(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should list all global skills."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls", "--global"])

        assert result.exit_code == 0
        assert "Global skills (2)" in result.output
        assert "skill-1" in result.output
        assert "skill-2" in result.output

    def test_ls_available_all(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should list all available skills when none in project."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls", "--available"])

        assert result.exit_code == 0
        assert "Available skills (2)" in result.output
        assert "skill-1" in result.output
        assert "skill-2" in result.output

    def test_ls_available_filtered(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should filter out skills already in project."""
        monkeypatch.chdir(mock_project_dir)

        # Add skill-1 to project
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        skill1_link = project_skills / "skill-1"
        os.symlink(mock_global_skills / "skill-1", skill1_link, target_is_directory=True)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls", "--available"])

        assert result.exit_code == 0
        assert "Available skills (1)" in result.output
        assert "skill-2" in result.output
        assert "skill-1" not in result.output

    def test_ls_available_none(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show message when all skills are in project."""
        monkeypatch.chdir(mock_project_dir)

        # Add both skills to project
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)

        for skill_name in ["skill-1", "skill-2"]:
            skill_link = project_skills / skill_name
            os.symlink(mock_global_skills / skill_name, skill_link, target_is_directory=True)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["ls", "--available"])

        assert result.exit_code == 0
        assert "No skills available to add" in result.output

    def test_ls_global_not_found(self, runner, tmp_path, monkeypatch):
        """Should show error when global directory doesn't exist."""
        monkeypatch.chdir(tmp_path)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", tmp_path / "nonexistent"):
            result = runner.invoke(cli, ["ls", "--global"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()


class TestAddCommand:
    """Tests for 'skillman add' command."""

    def test_add_skill_success(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should add skill to project."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["add", "skill-1"])

        assert result.exit_code == 0
        assert "Added skill 'skill-1'" in result.output

        # Verify symlink was created
        project_skill = mock_project_dir / ".claude" / "skills" / "skill-1"
        assert project_skill.exists()
        assert project_skill.is_symlink()

    def test_add_skill_not_found(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show error when skill doesn't exist in global."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["add", "nonexistent"])

        assert result.exit_code == 0
        assert "not found in global repository" in result.output

    def test_add_skill_already_exists(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show warning when skill already in project."""
        monkeypatch.chdir(mock_project_dir)

        # Add skill first time
        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            runner.invoke(cli, ["add", "skill-1"])

            # Try to add again
            result = runner.invoke(cli, ["add", "skill-1"])

        assert result.exit_code == 0
        assert "already exists in project" in result.output

    def test_add_invalid_skill(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show error when directory doesn't have SKILL.md."""
        monkeypatch.chdir(mock_project_dir)

        # Create directory without SKILL.md
        invalid_skill = mock_global_skills / "invalid"
        invalid_skill.mkdir()

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["add", "invalid"])

        assert result.exit_code == 0
        assert "not a valid skill" in result.output


class TestRemoveCommand:
    """Tests for 'skillman remove' command."""

    def test_remove_skill_success(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should remove skill from project."""
        monkeypatch.chdir(mock_project_dir)

        # Add skill first
        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            runner.invoke(cli, ["add", "skill-1"])

            # Remove it
            result = runner.invoke(cli, ["remove", "skill-1"])

        assert result.exit_code == 0
        assert "Removed skill 'skill-1'" in result.output

        # Verify symlink was removed
        project_skill = mock_project_dir / ".claude" / "skills" / "skill-1"
        assert not project_skill.exists()

    def test_remove_skill_not_found(self, runner, mock_project_dir, monkeypatch):
        """Should show warning when skill not in project."""
        monkeypatch.chdir(mock_project_dir)

        result = runner.invoke(cli, ["remove", "nonexistent"])

        assert result.exit_code == 0
        assert "not found in project" in result.output

    def test_remove_non_symlink(self, runner, mock_project_dir, monkeypatch):
        """Should warn when trying to remove non-symlink."""
        monkeypatch.chdir(mock_project_dir)

        # Create a regular directory (not a symlink)
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        regular_dir = project_skills / "regular"
        regular_dir.mkdir()
        (regular_dir / "SKILL.md").write_text("# Regular")

        result = runner.invoke(cli, ["remove", "regular"])

        assert result.exit_code == 0
        assert "not a symlink" in result.output


class TestSaveCommand:
    """Tests for 'skillman save' command."""

    def test_save_skill_success(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should save a project skill to global repository."""
        monkeypatch.chdir(mock_project_dir)

        # Create a local skill (not a symlink)
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        local_skill = project_skills / "my-local-skill"
        local_skill.mkdir()
        (local_skill / "SKILL.md").write_text(
            "---\nname: my-local-skill\ndescription: Local skill\n---\n# Local"
        )

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["save", "my-local-skill"])

        assert result.exit_code == 0
        assert "saved successfully" in result.output.lower()

        # Verify skill was moved to global repo
        global_skill = mock_global_skills / "my-local-skill"
        assert global_skill.exists()
        assert (global_skill / "SKILL.md").exists()

        # Verify symlink was created in project
        project_skill = project_skills / "my-local-skill"
        assert project_skill.exists()
        assert project_skill.is_symlink()
        assert project_skill.resolve() == global_skill

    def test_save_skill_not_found(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show error when skill not in project."""
        monkeypatch.chdir(mock_project_dir)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["save", "nonexistent"])

        assert result.exit_code == 0
        assert "not found in project" in result.output.lower()

    def test_save_skill_already_symlink(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show message when skill is already a symlink."""
        monkeypatch.chdir(mock_project_dir)

        # Create a symlink in project
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        skill_link = project_skills / "skill-1"
        os.symlink(mock_global_skills / "skill-1", skill_link, target_is_directory=True)

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["save", "skill-1"])

        assert result.exit_code == 0
        assert "already in global repository" in result.output.lower()

    def test_save_skill_invalid(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should show error when skill has no SKILL.md."""
        monkeypatch.chdir(mock_project_dir)

        # Create invalid skill (no SKILL.md)
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        invalid_skill = project_skills / "invalid"
        invalid_skill.mkdir()

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            result = runner.invoke(cli, ["save", "invalid"])

        assert result.exit_code == 0
        assert "not a valid skill" in result.output.lower()

    def test_save_skill_overwrite_existing(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should ask for confirmation when skill exists in global repo."""
        monkeypatch.chdir(mock_project_dir)

        # Create a local skill
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        local_skill = project_skills / "skill-1"
        local_skill.mkdir()
        (local_skill / "SKILL.md").write_text(
            "---\nname: skill-1\ndescription: Modified\n---\n# Modified"
        )

        # skill-1 already exists in mock_global_skills
        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            # Answer "no" to overwrite
            result = runner.invoke(cli, ["save", "skill-1"], input="n\n")

        assert result.exit_code == 0
        assert "already exists" in result.output.lower()
        assert "Aborted" in result.output

    def test_save_skill_overwrite_confirmed(self, runner, mock_global_skills, mock_project_dir, monkeypatch):
        """Should overwrite when user confirms."""
        monkeypatch.chdir(mock_project_dir)

        # Create a local skill with different content
        project_skills = mock_project_dir / ".claude" / "skills"
        project_skills.mkdir(parents=True)
        local_skill = project_skills / "skill-1"
        local_skill.mkdir()
        (local_skill / "SKILL.md").write_text(
            "---\nname: skill-1\ndescription: Modified version\n---\n# Modified"
        )

        with patch("skillman.cli.DEFAULT_SKILLS_PATH", mock_global_skills):
            # Answer "yes" to overwrite
            result = runner.invoke(cli, ["save", "skill-1"], input="y\n")

        assert result.exit_code == 0
        assert "saved successfully" in result.output.lower()

        # Verify new version is in global repo
        global_skill = mock_global_skills / "skill-1"
        content = (global_skill / "SKILL.md").read_text()
        assert "Modified version" in content


class TestVersionCommand:
    """Tests for version flag."""

    def test_version(self, runner):
        """Should display version."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
        assert "skillman" in result.output.lower()
