from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class ProjectPaths:
    root: Path = PROJECT_ROOT
    asr_model: Path = PROJECT_ROOT / "models" / "asr_model" / "ASR_model"
    llm_model: Path = PROJECT_ROOT / "models" / "llm_model" / "Qwen2.5"
    tts_model: Path = PROJECT_ROOT / "models" / "tts_model" / "菲比"
    reference_audio: Path = PROJECT_ROOT / "resources" / "zh_vo_Main_Linaxita_2_1_10_26.wav"


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
        return cls(
            asr_path=str(paths.asr_model),
            llm_path=str(paths.llm_model),
            tts_model_dir=str(paths.tts_model),
            ref_audio_path=str(paths.reference_audio),
            ref_text="在此之前，请您务必继续享受旅居拉古那的时光。",
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
