"""
Color themes for Symphonium household staff output
"""

# Available color themes for the Symphonium ensemble
COLOR_THEMES = {
    "default": {"header": "blue", "response": "white", "description": "Classic blue headers with white text"},
    "claude_cyan": {
        "header": "bright_blue",
        "response": "bright_cyan",
        "description": "Claude Code inspired cyan tones",
    },
    "salmon_original": {
        "header": (255, 120, 100),
        "response": (255, 140, 120),
        "description": "Warm salmon tones - original version",
    },
    "salmon_bright": {
        "header": (255, 99, 71),  # Tomato
        "response": (255, 127, 80),  # Coral
        "description": "Bright vibrant salmon/coral colors",
    },
    "pastel_pink": {
        "header": (255, 182, 193),  # Light pink
        "response": (255, 192, 203),  # Pink
        "description": "Soft pastel pink tones",
    },
    "sunset_orange": {
        "header": (255, 165, 0),  # Orange
        "response": (255, 218, 185),  # Peach puff
        "description": "Warm sunset orange gradient",
    },
    "mint_green": {
        "header": (144, 238, 144),  # Light green
        "response": (152, 251, 152),  # Pale green
        "description": "Fresh mint green tones",
    },
    "lavender": {
        "header": (147, 112, 219),  # Medium purple
        "response": (221, 160, 221),  # Plum
        "description": "Soft lavender purple",
    },
    "ocean_blue": {
        "header": (30, 144, 255),  # Dodger blue
        "response": (135, 206, 250),  # Light sky blue
        "description": "Ocean-inspired blues",
    },
}


def get_theme_colors(theme_name: str = "salmon_original"):
    """Get colors for a specific theme"""
    theme = COLOR_THEMES.get(theme_name, COLOR_THEMES["salmon_original"])
    return theme["header"], theme["response"]


def list_themes():
    """List all available themes with descriptions"""
    for name, theme in COLOR_THEMES.items():
        print(f"{name}: {theme['description']}")


# Quick reference for your favorite combinations
FAVORITE_COLORS = {
    "salmon_soft": (255, 120, 100),  # Your preferred header color
    "salmon_response": (255, 140, 120),  # Your preferred response color
    "coral_bright": (255, 99, 71),  # Brighter alternative
    "coral_response": (255, 127, 80),  # Brighter response alternative
}
