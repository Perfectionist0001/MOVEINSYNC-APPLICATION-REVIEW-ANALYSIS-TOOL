"""
MoveInSync Configuration Loader
Validates and loads application metadata and theme taxonomy from JSON config files.
"""

import json
import os
import re
from typing import Dict, List, Any


def load_apps_config(filepath: str = "config/apps.json") -> Dict[str, Any]:
    """
    Loads and validates the application configuration.
    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If JSON syntax is invalid or required fields are missing.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Apps configuration file not found at: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in apps config '{filepath}': {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Apps config in '{filepath}' must be a JSON object, got {type(data).__name__}")

    if "apps" not in data or not isinstance(data["apps"], list) or len(data["apps"]) == 0:
        raise ValueError(f"Apps config in '{filepath}' must contain a non-empty 'apps' list")

    required_app_fields = {"app_id", "name", "role", "raw_reviews_file"}
    seen_ids = set()
    for idx, app_entry in enumerate(data["apps"]):
        if not isinstance(app_entry, dict):
            raise ValueError(f"App entry #{idx} in '{filepath}' must be an object")
        missing = required_app_fields - set(app_entry.keys())
        if missing:
            raise ValueError(f"App entry #{idx} in '{filepath}' is missing required fields: {sorted(missing)}")
        
        app_id = app_entry["app_id"]
        if not app_id or not isinstance(app_id, str):
            raise ValueError(f"App entry #{idx} has invalid 'app_id': {app_id}")
        if app_id in seen_ids:
            raise ValueError(f"Duplicate app_id detected in '{filepath}': {app_id}")
        seen_ids.add(app_id)

    return data


def load_taxonomy_config(filepath: str = "config/taxonomy.json") -> Dict[str, Any]:
    """
    Loads and validates the theme taxonomy configuration.
    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If JSON syntax is invalid, required fields are missing, or regex fails to compile.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Taxonomy configuration file not found at: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Malformed JSON in taxonomy config '{filepath}': {e}") from e

    if not isinstance(data, dict):
        raise ValueError(f"Taxonomy config in '{filepath}' must be a JSON object")

    if "themes" not in data or not isinstance(data["themes"], dict) or len(data["themes"]) == 0:
        raise ValueError(f"Taxonomy config in '{filepath}' must contain a non-empty 'themes' object")

    if "fallback_theme" not in data or not isinstance(data["fallback_theme"], dict):
        raise ValueError(f"Taxonomy config in '{filepath}' missing 'fallback_theme' object")

    fb = data["fallback_theme"]
    if "id" not in fb or "display_name" not in fb:
        raise ValueError(f"fallback_theme in '{filepath}' must have 'id' and 'display_name'")

    if "priority_order" not in data or not isinstance(data["priority_order"], list):
        raise ValueError(f"Taxonomy config in '{filepath}' missing 'priority_order' list")

    # Validate each theme and its patterns
    for theme_id, theme_meta in data["themes"].items():
        if not isinstance(theme_meta, dict):
            raise ValueError(f"Theme '{theme_id}' definition must be an object")
        if "display_name" not in theme_meta:
            raise ValueError(f"Theme '{theme_id}' is missing 'display_name'")
        if "patterns" not in theme_meta or not isinstance(theme_meta["patterns"], list):
            raise ValueError(f"Theme '{theme_id}' is missing 'patterns' list")

        # Verify all regexes compile
        for pattern in theme_meta["patterns"]:
            try:
                re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{pattern}' in theme '{theme_id}': {e}") from e

    return data


def get_theme_patterns(taxonomy_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Returns a dict mapping theme_id -> list of regex pattern strings."""
    return {t_id: meta["patterns"] for t_id, meta in taxonomy_data["themes"].items()}


def get_theme_display_names(taxonomy_data: Dict[str, Any]) -> Dict[str, str]:
    """Returns a dict mapping theme_id -> display_name string, including fallback."""
    names = {t_id: meta["display_name"] for t_id, meta in taxonomy_data["themes"].items()}
    fb = taxonomy_data.get("fallback_theme", {})
    if "id" in fb and "display_name" in fb:
        names[fb["id"]] = fb["display_name"]
    return names


def get_priority_order(taxonomy_data: Dict[str, Any]) -> List[str]:
    """Returns the priority order list of theme IDs."""
    return list(taxonomy_data.get("priority_order", []))


def compile_taxonomy_rules(taxonomy_data: Dict[str, Any]) -> Dict[str, re.Pattern]:
    """Compiles all theme patterns into case-insensitive regex objects."""
    compiled = {}
    for theme_id, meta in taxonomy_data["themes"].items():
        patterns = meta.get("patterns", [])
        if patterns:
            combined = "|".join(patterns)
            compiled[theme_id] = re.compile(combined, re.IGNORECASE)
    return compiled
