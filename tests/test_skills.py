"""Tests for skills.py - SkillManager functionality."""

from pathlib import Path
import pytest

from skillman.skills import SkillManager


@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestSkillManager:
    """Tests for SkillManager class."""

    def test_get_skills_from_valid_directory(self, fixtures_dir):
        """Should discover all valid skills in directory."""
        manager = SkillManager(fixtures_dir)
        skills = manager.get_skills()

        # Should find 3 skills (valid-skill, no-description, skill-with-extras)
        # invalid-skill doesn't have SKILL.md so it's ignored
        assert len(skills) == 3

        skill_names = [s["name"] for s in skills]
        assert "valid-skill" in skill_names
        assert "no-description" in skill_names
        assert "skill-with-extras" in skill_names

    def test_get_skills_from_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        manager = SkillManager(Path("/nonexistent/path"))
        skills = manager.get_skills()

        assert skills == []

    def test_parse_skill_with_description(self, fixtures_dir):
        """Should extract description from frontmatter."""
        manager = SkillManager(fixtures_dir)
        skill = manager._parse_skill(fixtures_dir / "valid-skill")

        assert skill is not None
        assert skill["name"] == "valid-skill"
        assert skill["description"] == "This is a valid test skill with description"
        assert skill["has_scripts"] is False
        assert skill["has_examples"] is False
        assert skill["has_resources"] is False

    def test_parse_skill_without_description(self, fixtures_dir):
        """Should handle skill without description in frontmatter."""
        manager = SkillManager(fixtures_dir)
        skill = manager._parse_skill(fixtures_dir / "no-description")

        assert skill is not None
        assert skill["name"] == "no-description"
        assert skill["description"] is None

    def test_parse_skill_with_extras(self, fixtures_dir):
        """Should detect scripts, examples, and resources directories."""
        manager = SkillManager(fixtures_dir)
        skill = manager._parse_skill(fixtures_dir / "skill-with-extras")

        assert skill is not None
        assert skill["name"] == "skill-with-extras"
        assert skill["has_scripts"] is True
        assert skill["has_examples"] is True
        assert skill["has_resources"] is True

    def test_parse_skill_without_skill_md(self, fixtures_dir):
        """Should return None for directory without SKILL.md."""
        manager = SkillManager(fixtures_dir)
        skill = manager._parse_skill(fixtures_dir / "invalid-skill")

        assert skill is None

    def test_parse_skill_path_format(self, fixtures_dir):
        """Should return absolute path as string."""
        manager = SkillManager(fixtures_dir)
        skill = manager._parse_skill(fixtures_dir / "valid-skill")

        assert skill is not None
        assert isinstance(skill["path"], str)
        assert skill["path"] == str(fixtures_dir / "valid-skill")

    def test_extract_description_with_quotes(self, tmp_path):
        """Should handle descriptions with quotes in frontmatter."""
        skill_dir = tmp_path / "quoted-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            '---\n'
            'description: "This has double quotes"\n'
            '---\n'
            '# Skill\n'
        )

        manager = SkillManager(tmp_path)
        skill = manager._parse_skill(skill_dir)

        assert skill["description"] == "This has double quotes"

    def test_extract_description_with_single_quotes(self, tmp_path):
        """Should handle descriptions with single quotes in frontmatter."""
        skill_dir = tmp_path / "single-quoted-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "description: 'This has single quotes'\n"
            "---\n"
            "# Skill\n"
        )

        manager = SkillManager(tmp_path)
        skill = manager._parse_skill(skill_dir)

        assert skill["description"] == "This has single quotes"

    def test_extract_description_no_frontmatter(self, tmp_path):
        """Should return None for SKILL.md without frontmatter."""
        skill_dir = tmp_path / "no-frontmatter"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Just a heading\n\nNo frontmatter here.")

        manager = SkillManager(tmp_path)
        skill = manager._parse_skill(skill_dir)

        assert skill["description"] is None
