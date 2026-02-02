"""Tests for config.py - Configuration management."""

from pathlib import Path
import pytest

from skillman import config


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    """Create a temporary config directory and patch config module."""
    config_dir = tmp_path / ".claude" / "skillman"
    config_file = config_dir / "config.toml"
    default_skills = config_dir / "skills"

    # Patch the config module constants
    monkeypatch.setattr(config, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config, "DEFAULT_SKILLS_PATH", default_skills)

    return {
        "config_dir": config_dir,
        "config_file": config_file,
        "default_skills": default_skills,
    }


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_returns_dict_with_skills_paths(self, temp_config_dir):
        """Should return dict with skills_paths key."""
        default = config.get_default_config()

        assert isinstance(default, dict)
        assert "skills_paths" in default
        assert isinstance(default["skills_paths"], list)

    def test_default_has_one_path(self, temp_config_dir):
        """Should have exactly one default path."""
        default = config.get_default_config()

        assert len(default["skills_paths"]) == 1

    def test_default_path_is_skillman_skills(self, temp_config_dir):
        """Default path should be ~/.claude/skillman/skills."""
        default = config.get_default_config()

        assert str(temp_config_dir["default_skills"]) in default["skills_paths"][0]


class TestEnsureConfigExists:
    """Tests for ensure_config_exists function."""

    def test_creates_config_dir_if_not_exists(self, temp_config_dir):
        """Should create config directory if it doesn't exist."""
        assert not temp_config_dir["config_dir"].exists()

        config.ensure_config_exists()

        assert temp_config_dir["config_dir"].exists()

    def test_creates_config_file_if_not_exists(self, temp_config_dir):
        """Should create config file with defaults if it doesn't exist."""
        assert not temp_config_dir["config_file"].exists()

        config.ensure_config_exists()

        assert temp_config_dir["config_file"].exists()

    def test_creates_default_skills_dir(self, temp_config_dir):
        """Should create default skills directory."""
        assert not temp_config_dir["default_skills"].exists()

        config.ensure_config_exists()

        assert temp_config_dir["default_skills"].exists()

    def test_returns_config_path(self, temp_config_dir):
        """Should return path to config file."""
        result = config.ensure_config_exists()

        assert result == temp_config_dir["config_file"]

    def test_does_not_overwrite_existing_config(self, temp_config_dir):
        """Should not overwrite existing config file."""
        # Create config manually first
        temp_config_dir["config_dir"].mkdir(parents=True)
        temp_config_dir["config_file"].write_text('skills_paths = ["/custom/path"]\n')

        config.ensure_config_exists()

        content = temp_config_dir["config_file"].read_text()
        assert "/custom/path" in content


class TestLoadConfig:
    """Tests for load_config function."""

    def test_loads_default_config(self, temp_config_dir):
        """Should load default config when no file exists."""
        loaded = config.load_config()

        assert "skills_paths" in loaded
        assert len(loaded["skills_paths"]) == 1

    def test_loads_existing_config(self, temp_config_dir):
        """Should load existing config file."""
        temp_config_dir["config_dir"].mkdir(parents=True)
        temp_config_dir["config_file"].write_text(
            'skills_paths = ["/path/one", "/path/two"]\n'
        )

        loaded = config.load_config()

        assert loaded["skills_paths"] == ["/path/one", "/path/two"]


class TestGetSkillsPaths:
    """Tests for get_skills_paths function."""

    def test_returns_list_of_paths(self, temp_config_dir):
        """Should return list of Path objects."""
        paths = config.get_skills_paths()

        assert isinstance(paths, list)
        assert all(isinstance(p, Path) for p in paths)

    def test_expands_tilde(self, temp_config_dir):
        """Should expand ~ in paths."""
        temp_config_dir["config_dir"].mkdir(parents=True)
        temp_config_dir["config_file"].write_text(
            'skills_paths = ["~/my-skills"]\n'
        )

        paths = config.get_skills_paths()

        # Should not contain ~ after expansion
        assert not any("~" in str(p) for p in paths)
        assert paths[0] == Path.home() / "my-skills"

    def test_returns_default_path(self, temp_config_dir):
        """Should return default skills path when using defaults."""
        paths = config.get_skills_paths()

        assert len(paths) == 1
        assert paths[0] == temp_config_dir["default_skills"]


class TestAddSkillsPath:
    """Tests for add_skills_path function."""

    def test_adds_new_path(self, temp_config_dir):
        """Should add new path to config."""
        config.ensure_config_exists()

        config.add_skills_path("/new/skills/path")

        loaded = config.load_config()
        assert "/new/skills/path" in loaded["skills_paths"]

    def test_does_not_add_duplicate(self, temp_config_dir):
        """Should not add duplicate path."""
        config.ensure_config_exists()
        config.add_skills_path("/new/path")
        config.add_skills_path("/new/path")

        loaded = config.load_config()
        count = loaded["skills_paths"].count("/new/path")
        assert count == 1

    def test_expands_tilde_when_adding(self, temp_config_dir):
        """Should expand ~ when adding path."""
        config.ensure_config_exists()

        config.add_skills_path("~/my-skills")

        loaded = config.load_config()
        expanded = str(Path.home() / "my-skills")
        assert expanded in loaded["skills_paths"]


class TestRemoveSkillsPath:
    """Tests for remove_skills_path function."""

    def test_removes_existing_path(self, temp_config_dir):
        """Should remove existing path from config."""
        temp_config_dir["config_dir"].mkdir(parents=True)
        temp_config_dir["config_file"].write_text(
            'skills_paths = ["/path/one", "/path/two"]\n'
        )

        result = config.remove_skills_path("/path/one")

        assert result is True
        loaded = config.load_config()
        assert "/path/one" not in loaded["skills_paths"]
        assert "/path/two" in loaded["skills_paths"]

    def test_returns_false_for_nonexistent_path(self, temp_config_dir):
        """Should return False when path doesn't exist."""
        config.ensure_config_exists()

        result = config.remove_skills_path("/nonexistent/path")

        assert result is False

    def test_handles_tilde_expansion(self, temp_config_dir):
        """Should handle ~ expansion when removing."""
        expanded = str(Path.home() / "my-skills")
        temp_config_dir["config_dir"].mkdir(parents=True)
        temp_config_dir["config_file"].write_text(
            f'skills_paths = ["{expanded}"]\n'
        )

        result = config.remove_skills_path("~/my-skills")

        assert result is True
        loaded = config.load_config()
        assert expanded not in loaded["skills_paths"]
