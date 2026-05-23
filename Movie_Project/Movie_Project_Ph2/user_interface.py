import os


class Bcolors:
    """Utility class to represent colors on the terminal."""

    HEADER = "\033[95m"
    MENU_TEXT = "\033[94m"
    OKCYAN = "\033[96m"
    INPUT_TEXT = "\033[92m"
    WARNING = "\033[93m"
    BLINKING = "\033[5m"
    FAIL = "\033[91m"
    LISTING = "\033[0m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

def clear_screen():
    """
    Clean the screen before showing the menu. Does not seem to work well though on this terminal
    """
    if os.name == "nt":
        os.system("cls")
    else:
        # fallback if TERM not set
        if "TERM" in os.environ:
            os.system("clear")
        else:
            print("\n" * 100)
