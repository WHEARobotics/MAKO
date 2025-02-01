"""
Module of constants related to the operator interface  
"""
from dataclasses import dataclass

# User Interface (UI) and control
@dataclass(frozen=True) # Tells Python that this class's variables can't be changed.
class UserInterface:
    """Constants related to human interaction."""
    DRIVE_SLOWER: float = 4.0 # Factor to divide the drive commands to slow things down for safety.
    XBOX_PORT: int = 2        # USB port number for the Xbox controller on Rod's computer.
