import questionary
from questionary import Style

THEMES = {
    "Red": "#FF5555",
    "Green": "#50FA7B",
    "Blue": "#61AFEF",
    "Yellow": "#F1FA8C",
    "Purple": "#BD93F9",
}

def choose_theme():
    theme = questionary.select(
        "Choose your theme color:",
        choices=[
            "Red",
            "Green",
            "Blue",
            "Yellow",
            "Purple"
        ],
        default="Blue"
    ).ask()

    return theme

def create_style(theme):
    color = THEMES[theme]

    return Style([
        ("qmark", f"fg:{color} bold"),
        ("question", f"fg:{color} bold"),
        ("pointer", f"fg:{color} bold"),
        ("highlighted", f"fg:{color} bold"),
        ("selected", f"fg:{color}"),
        ("answer", f"fg:{color} bold"),
    ])