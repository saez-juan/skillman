"""Skills management functionality."""

import os
from pathlib import Path
from typing import List, Dict, Optional
import re


class SkillManager:
    """Manages Claude skills discovery and parsing."""
    
    def __init__(self, skills_dir: Path):
        """
        Initialize the SkillManager.
        
        Args:
            skills_dir: Path to the skills directory
        """
        self.skills_dir = Path(skills_dir)
    
    def get_skills(self) -> List[Dict[str, any]]:
        """
        Discover and parse all skills in the skills directory.
        
        Returns:
            List of skill dictionaries with metadata
        """
        skills = []
        
        if not self.skills_dir.exists():
            return skills
        
        # Iterate through subdirectories
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                skill_info = self._parse_skill(item)
                if skill_info:
                    skills.append(skill_info)
        
        return skills
    
    def _parse_skill(self, skill_path: Path) -> Optional[Dict[str, any]]:
        """
        Parse a skill directory and extract metadata.
        
        Args:
            skill_path: Path to the skill directory
            
        Returns:
            Dictionary with skill metadata or None if invalid
        """
        skill_md = skill_path / "SKILL.md"
        
        # A valid skill must have a SKILL.md file
        if not skill_md.exists():
            return None
        
        # Parse SKILL.md for metadata
        name = skill_path.name
        description = self._extract_description(skill_md)
        
        # Check for additional directories
        has_scripts = (skill_path / "scripts").exists()
        has_examples = (skill_path / "examples").exists()
        has_resources = (skill_path / "resources").exists()
        
        return {
            "name": name,
            "description": description,
            "path": str(skill_path),
            "has_scripts": has_scripts,
            "has_examples": has_examples,
            "has_resources": has_resources,
        }
    
    def _extract_description(self, skill_md: Path) -> Optional[str]:
        """
        Extract description from SKILL.md frontmatter.
        
        Args:
            skill_md: Path to SKILL.md file
            
        Returns:
            Description string or None
        """
        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Look for YAML frontmatter
            frontmatter_match = re.match(
                r"^---\s*\n(.*?)\n---\s*\n",
                content,
                re.DOTALL
            )
            
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                
                # Extract description field
                desc_match = re.search(
                    r"description:\s*(.+?)(?:\n|$)",
                    frontmatter,
                    re.IGNORECASE
                )
                
                if desc_match:
                    description = desc_match.group(1).strip()
                    # Remove quotes if present
                    description = description.strip('"\'')
                    return description
            
            return None
            
        except Exception:
            return None
