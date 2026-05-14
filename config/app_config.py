from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_ROOT = PROJECT_ROOT / "resources"
PROMPT_WAV_CONFIG = RESOURCES_ROOT / "prompt_wav.json"
USER_SETTINGS_PATH = PROJECT_ROOT / "config" / "user_settings.json"
APP_VERSION = "0.2.0"
APP_AUTHOR = "Nyzeep"
PROJECT_URL = "https://github.com/Nyzeep/LumiMate"
APP_PHILOSOPHY = "A spatial AI companion system with emotion, ritual, and breath."
UPDATE_MANIFEST_URL = ""
DEFAULT_REF_WAV = "zh_vo_Main_Linaxita_2_1_10_26.wav"
DEFAULT_REF_TEXT = "在每一个安静的夜里，Lumi 都会在这里等你。"
DEFAULT_AMBIENT_MODE = "quiet"
VALID_AMBIENT_MODES = {"quiet", "breath", "stream"}


def _normalize_ambient_mode(value: str) -> str:
    mode = str(value or DEFAULT_AMBIENT_MODE).strip().lower()
    return mode if mode in VALID_AMBIENT_MODES else DEFAULT_AMBIENT_MODE


def _reference_prompt() -> tuple[Path, str]:
    try:
        payload = json.loads(PROMPT_WAV_CONFIG.read_text(encoding="utf-8"))
        normal = payload.get("Normal", {})
        wav_name = str(normal.get("wav") or DEFAULT_REF_WAV)
        text = str(normal.get("text") or DEFAULT_REF_TEXT)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        wav_name = DEFAULT_REF_WAV
        text = DEFAULT_REF_TEXT

    wav_path = Path(wav_name)
    if not wav_path.is_absolute():
        wav_path = RESOURCES_ROOT / wav_path
    return wav_path, text


@dataclass(slots=True)
class ProjectPaths:
    root: Path = PROJECT_ROOT
    asr_model: Path = PROJECT_ROOT / "models" / "asr_model" / "ASR_model"
    llm_model: Path = PROJECT_ROOT / "models" / "llm_model" / "Qwen2.5"
    tts_model: Path = PROJECT_ROOT / "models" / "tts_model" / "菲比"
    reference_audio: Path = PROJECT_ROOT / "resources" / DEFAULT_REF_WAV


@dataclass(slots=True)
class UserSettings:
    language: str = "zh-CN"
    check_update_on_startup: bool = False
    startup_page: str = "home"
    reduce_motion: bool = False
    ambient_mode: str = DEFAULT_AMBIENT_MODE

    @classmethod
    def load(cls) -> "UserSettings":
        try:
            payload = json.loads(USER_SETTINGS_PATH.read_text(encoding="utf-8"))
            return cls(
                language=str(payload.get("language") or "zh-CN"),
                check_update_on_startup=bool(payload.get("check_update_on_startup", False)),
                startup_page=str(payload.get("startup_page") or "home"),
                reduce_motion=bool(payload.get("reduce_motion", False)),
                ambient_mode=_normalize_ambient_mode(payload.get("ambient_mode", DEFAULT_AMBIENT_MODE)),
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return cls()

    def save(self) -> bool:
        try:
            USER_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            USER_SETTINGS_PATH.write_text(
                json.dumps(
                    {
                        "language": self.language,
                        "check_update_on_startup": self.check_update_on_startup,
                        "startup_page": self.startup_page,
                        "reduce_motion": self.reduce_motion,
                        "ambient_mode": _normalize_ambient_mode(self.ambient_mode),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            return True
        except OSError:
            return False


@dataclass(slots=True)
class ReferenceAudioConfig:
    path: str
    text: str

    def validate(self) -> list[str]:
        issues: list[str] = []
        audio_path = Path(self.path)
        if not audio_path.exists():
            issues.append(f"Reference audio not found: {audio_path}")
        elif audio_path.suffix.lower() not in {".wav", ".mp3", ".flac"}:
            issues.append("Reference audio must be .wav, .mp3, or .flac.")
        if not self.text.strip():
            issues.append("Reference audio text cannot be empty.")
        return issues


@dataclass(slots=True)
class AssistantConfig:
    asr_path: str
    llm_path: str
    tts_model_dir: str
    ref_audio_path: str
    ref_text: str
    tts_character: str = "菲比"
    sample_rate: int = 16000
    chunk_sec: int = 3
    energy_threshold: float = 0.005
    max_new_tokens: int = 100
    temperature: float = 0.6
    top_p: float = 0.9
    repetition_penalty: float = 1.1

    @classmethod
    def defaults(cls) -> "AssistantConfig":
        paths = ProjectPaths()
        reference_audio, reference_text = _reference_prompt()
        return cls(
            asr_path=str(paths.asr_model),
            llm_path=str(paths.llm_model),
            tts_model_dir=str(paths.tts_model),
            ref_audio_path=str(reference_audio if reference_audio.exists() else paths.reference_audio),
            ref_text=reference_text,
        )

    def to_core_dict(self) -> dict:
        return {
            "asr_path": self.asr_path,
            "llm_path": self.llm_path,
            "tts_character": self.tts_character,
            "tts_model_dir": self.tts_model_dir,
            "ref_audio_path": self.ref_audio_path,
            "ref_text": self.ref_text,
            "sample_rate": self.sample_rate,
            "chunk_sec": self.chunk_sec,
            "energy_threshold": self.energy_threshold,
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
        }

    def reference_audio(self) -> ReferenceAudioConfig:
        return ReferenceAudioConfig(self.ref_audio_path, self.ref_text)
