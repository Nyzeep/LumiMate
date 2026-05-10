from __future__ import annotations

import gc
from collections.abc import Callable
from typing import Any

from config import ReferenceAudioConfig


class ModelManager:
    def __init__(self, log: Callable[[str], None]):
        self.log = log
        self.asr: Any = None
        self.tokenizer: Any = None
        self.llm: Any = None
        self.genie: Any = None
        self.tts_ready = False

    def load(self, config: dict, progress_callback: Callable[[int, int, str], None] | None = None) -> bool:
        issues = ReferenceAudioConfig(config.get("ref_audio_path", ""), config.get("ref_text", "")).validate()
        if issues:
            for issue in issues:
                self.log(issue)
            return False

        try:
            import torch
            from qwen_asr import Qwen3ASRModel
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import genie_tts as genie
        except Exception as exc:
            self.log(f"Model dependency import failed: {exc}")
            return False

        try:
            self.genie = genie

            if progress_callback:
                progress_callback(1, 4, "Loading ASR model...")
            self.asr = Qwen3ASRModel.from_pretrained(
                config["asr_path"],
                dtype=torch.bfloat16,
                device_map="auto",
                max_new_tokens=256,
            )
            self.log("ASR model loaded.")

            if progress_callback:
                progress_callback(2, 4, "Loading LLM model...")
            self.tokenizer = AutoTokenizer.from_pretrained(config["llm_path"], trust_remote_code=True)
            self.llm = AutoModelForCausalLM.from_pretrained(
                config["llm_path"],
                device_map="auto",
                torch_dtype="auto",
                trust_remote_code=True,
            )
            device = getattr(self.llm, "device", "auto")
            self.log(f"LLM model loaded on {device}.")

            if progress_callback:
                progress_callback(3, 4, "Initializing TTS...")
            genie.load_character(
                character_name=config["tts_character"],
                onnx_model_dir=config["tts_model_dir"],
                language="zh",
            )

            if progress_callback:
                progress_callback(4, 4, "Binding reference audio...")
            genie.set_reference_audio(
                character_name=config["tts_character"],
                audio_path=config["ref_audio_path"],
                audio_text=config["ref_text"],
            )
            self.tts_ready = True
            self.log("TTS initialized.")
            return True
        except Exception as exc:
            self.log(f"Model loading failed: {exc}")
            self.unload()
            return False

    def switch(self, config: dict, progress_callback: Callable[[int, int, str], None] | None = None) -> bool:
        self.unload()
        return self.load(config, progress_callback)

    def unload(self) -> None:
        try:
            self.asr = None
            self.tokenizer = None
            self.llm = None
            self.tts_ready = False
            self.genie = None
        except Exception as exc:
            self.log(f"Model release failed: {exc}")
        finally:
            self.clear_cache()

    def clear_cache(self) -> None:
        try:
            gc.collect()
            try:
                import torch
            except Exception:
                return
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            self.log("Cache released.")
        except Exception as exc:
            self.log(f"Cache release failed: {exc}")
