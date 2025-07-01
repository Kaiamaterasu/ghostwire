"""
Ghostwire - Encrypted P2P Communication Tool with Steganographic Capabilities

This package provides secure, encrypted peer-to-peer communication with the ability
to hide messages in images using steganography.

Author: Kaiamaterasu
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Kaiamaterasu"
__description__ = "🔒 Encrypted P2P Communication Tool with Steganographic Capabilities"

# Import main modules for easy access
from .ghostwire_simple import GhostwireServer, send_message
from .ghostwire_steganography import GhostwireSteganography

__all__ = [
    "GhostwireServer",
    "send_message", 
    "GhostwireSteganography"
]
