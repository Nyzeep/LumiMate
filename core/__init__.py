from .bootstrap import AppBootstrap, BootstrapResult
from .i18n import tr
from .integrity import IntegrityVerifier

__all__ = ["AppBootstrap", "BootstrapResult", "IntegrityVerifier", "VoiceAssistant", "tr"]


def __getattr__(name: str):
    if name == "VoiceAssistant":
        from .voice_assistant import VoiceAssistant

        return VoiceAssistant
    raise AttributeError(name)
