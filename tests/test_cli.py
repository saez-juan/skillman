"""Tests for cli.py - CLI commands."""

from pathlib import Path
import pytest
from click.testing import CliRunner

from skillman.cli import cli


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestListCommand:
    """Tests for 'skillman ls' command."""

    def test_ls_with_valid_path(self, runner, fixtures_dir):
        """Should list skills from specified directory."""
        result = runner.invoke(cli, ["ls", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        assert "valid-skill" in result.output
        assert "no-description" in result.output
        assert "skill-with-extras" in result.output
        # invalid-skill should NOT appear (no SKILL.md)
        assert "invalid-skill" not in result.output

    def test_ls_with_nonexistent_path(self, runner):
        """Should show error message for nonexistent directory."""
        result = runner.invoke(cli, ["ls", "--path", "/nonexistent/path"])

        assert result.exit_code == 0  # Click doesn't exit with error by default
        assert "not found" in result.output.lower()

    def test_ls_with_empty_directory(self, runner, tmp_path):
        """Should show message when no skills found."""
        result = runner.invoke(cli, ["ls", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "no skills found" in result.output.lower()

    def test_ls_simple_output(self, runner, fixtures_dir):
        """Should display simple list without --detailed flag."""
        result = runner.invoke(cli, ["ls", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        # Should show skill names
        assert "valid-skill" in result.output
        # Should show descriptions
        assert "This is a valid test skill with description" in result.output
        # Should show location
        assert str(fixtures_dir) in result.output

    def test_ls_detailed_output(self, runner, fixtures_dir):
        """Should display detailed information with --detailed flag."""
        result = runner.invoke(cli, ["ls", "--detailed", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        # Should show skill names
        assert "valid-skill" in result.output
        # Should show paths
        assert "Path:" in result.output
        # Should show extras for skill-with-extras
        assert "Contains:" in result.output
        assert "scripts" in result.output

    def test_ls_detailed_shows_extras(self, runner, fixtures_dir):
        """Should list scripts/examples/resources in detailed mode."""
        result = runner.invoke(cli, ["ls", "--detailed", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        # skill-with-extras should show all extras
        output_lines = result.output
        assert "scripts" in output_lines
        assert "examples" in output_lines
        assert "resources" in output_lines

    def test_ls_with_relative_path(self, runner, fixtures_dir, tmp_path, monkeypatch):
        """Should handle relative paths correctly."""
        # Change to temp directory
        monkeypatch.chdir(fixtures_dir.parent)

        result = runner.invoke(cli, ["ls", "--path", "./fixtures"])

        assert result.exit_code == 0
        assert "valid-skill" in result.output

    def test_ls_short_flag(self, runner, fixtures_dir):
        """Should accept -p as shorthand for --path."""
        result = runner.invoke(cli, ["ls", "-p", str(fixtures_dir)])

        assert result.exit_code == 0
        assert "valid-skill" in result.output

    def test_ls_short_detailed_flag(self, runner, fixtures_dir):
        """Should accept -d as shorthand for --detailed."""
        result = runner.invoke(cli, ["ls", "-d", "-p", str(fixtures_dir)])

        assert result.exit_code == 0
        assert "Path:" in result.output

    def test_ls_no_description_shown_as_no_description(self, runner, fixtures_dir):
        """Should show 'No description' for skills without description."""
        result = runner.invoke(cli, ["ls", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        # The no-description skill should appear but with fallback text
        assert "no-description" in result.output

    def test_ls_skills_sorted_alphabetically(self, runner, fixtures_dir):
        """Should display skills in alphabetical order."""
        result = runner.invoke(cli, ["ls", "--path", str(fixtures_dir)])

        assert result.exit_code == 0

        # Find positions of skill names in output
        output = result.output
        pos_no_desc = output.find("no-description")
        pos_skill_extras = output.find("skill-with-extras")
        pos_valid = output.find("valid-skill")

        # All should be found
        assert pos_no_desc > 0
        assert pos_skill_extras > 0
        assert pos_valid > 0

        # Should be in alphabetical order
        assert pos_no_desc < pos_skill_extras < pos_valid

    def test_ls_count_displayed(self, runner, fixtures_dir):
        """Should show count of skills found."""
        result = runner.invoke(cli, ["ls", "--path", str(fixtures_dir)])

        assert result.exit_code == 0
        # Should show "Skills (3):" or similar
        assert "(3)" in result.output

    def test_version_option(self, runner):
        """Should display version with --version flag."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
        assert "skillman" in result.output.lower()
