from __future__ import annotations

import re
import threading

import numpy as np


class VoiceAssistant:
    def __init__(self, config, on_user_text=None, on_assistant_text=None, on_log=None, on_state=None):
        self.config = config
        self.on_user_text = on_user_text
        self.on_assistant_text = on_assistant_text
        self.on_log = on_log
        self.on_state = on_state
        self.running = False
        self.thread: threading.Thread | None = None
        self.asr = None
        self.tokenizer = None
        self.llm = None
        self.tts_ready = False
        self.messages = []
        self.genie = None
        self._lock = threading.RLock()
        self._response_lock = threading.RLock()

    def log(self, message: str) -> None:
        if self.on_log:
            self.on_log(message)
        else:
            print(message)

    def state(self, state: str, message: str) -> None:
        if self.on_state:
            self.on_state(state, message)

    def load_models(self, progress_callback=None) -> bool:
        try:
            import torch
            from qwen_asr import Qwen3ASRModel
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import genie_tts as genie
        except Exception as exc:
            self.log(f"模型依赖导入失败：{exc}")
            return False

        try:
            self.genie = genie

            if progress_callback:
                progress_callback(1, 4, "正在加载 ASR 模型。")
            self.asr = Qwen3ASRModel.from_pretrained(
                self.config["asr_path"],
                dtype=torch.bfloat16,
                device_map="auto",
                max_new_tokens=256,
            )
            self.log("ASR 模型加载完成。")

            if progress_callback:
                progress_callback(2, 4, "正在加载 LLM 模型。")
            self.tokenizer = AutoTokenizer.from_pretrained(self.config["llm_path"], trust_remote_code=True)
            self.llm = AutoModelForCausalLM.from_pretrained(
                self.config["llm_path"],
                device_map="auto",
                torch_dtype="auto",
                trust_remote_code=True,
            )
            device = getattr(self.llm, "device", "auto")
            self.log(f"LLM 模型加载完成，设备：{device}")

            if progress_callback:
                progress_callback(3, 4, "正在初始化 TTS。")
            genie.load_character(
                character_name=self.config["tts_character"],
                onnx_model_dir=self.config["tts_model_dir"],
                language="zh",
            )

            if progress_callback:
                progress_callback(4, 4, "正在绑定参考音频。")
            genie.set_reference_audio(
                character_name=self.config["tts_character"],
                audio_path=self.config["ref_audio_path"],
                audio_text=self.config["ref_text"],
            )
            self.tts_ready = True
            self.log("TTS 初始化完成。")
            return True
        except Exception as exc:
            self.log(f"模型加载失败：{exc}")
            return False

    def llm_generate(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        prompt = self.tokenizer.apply_chat_template(self.messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.llm.device)
        outputs = self.llm.generate(
            **inputs,
            max_new_tokens=self.config.get("max_new_tokens", 100),
            do_sample=True,
            temperature=self.config.get("temperature", 0.6),
            top_p=self.config.get("top_p", 0.9),
            repetition_penalty=self.config.get("repetition_penalty", 1.1),
            pad_token_id=self.tokenizer.eos_token_id,
        )
        response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        response = re.sub(r"<\|im_end\|>", "", response).strip()
        if len(response) > 100:
            response = response[:100]
        self.messages.append({"role": "assistant", "content": response})
        return response

    def respond_to_text(self, user_text: str, speak: bool = True, emit_user: bool = True) -> str:
        user_text = user_text.strip()
        if not user_text:
            return ""
        if not self.llm or not self.tokenizer:
            raise RuntimeError("模型还没有准备好。")

        if emit_user:
            self.log(f"你：{user_text}")
            if self.on_user_text:
                self.on_user_text(user_text)

        with self._response_lock:
            assistant_text = self.llm_generate(user_text)
            self.log(f"Lumi：{assistant_text}")
            if self.on_assistant_text:
                self.on_assistant_text(assistant_text)
            if speak:
                self.safe_tts(assistant_text)
            return assistant_text

    def safe_tts(self, text: str) -> None:
        if not text or not self.tts_ready or self.genie is None:
            return
        text = text.replace("嗯", "恩").replace("啊", "呀").replace("呃", "额")
        text = re.sub(r"[^\u4e00-\u9fa5，。！？、,.!?]", "", text)
        if len(text) < 2:
            text = "好的。"
        try:
            self.genie.tts(
                character_name=self.config["tts_character"],
                text=text,
                split_sentence=False,
                play=True,
                save_path=None,
            )
            self.genie.wait_for_playback_done()
        except Exception as exc:
            self.log(f"TTS 播放失败：{exc}")

    def has_energy(self, audio) -> bool:
        threshold = self.config.get("energy_threshold", 0.005)
        return np.sqrt(np.mean(audio**2)) > threshold

    def _run_loop(self) -> None:
        try:
            import sounddevice as sd
        except Exception as exc:
            self.log(f"录音设备初始化失败：{exc}")
            self.running = False
            return

        sample_rate = self.config["sample_rate"]
        chunk_sec = self.config["chunk_sec"]
        chunk_size = int(sample_rate * chunk_sec)

        while self.running:
            self.log(f"正在聆听...（{chunk_sec} 秒）")
            try:
                audio_data = sd.rec(chunk_size, samplerate=sample_rate, channels=1, dtype="float32")
                sd.wait()
                audio_data = audio_data.flatten()
            except Exception as exc:
                self.log(f"录音失败：{exc}")
                continue

            if not self.has_energy(audio_data):
                self.log("没有听到清晰的声音。")
                continue

            try:
                result_list = self.asr.transcribe((audio_data, sample_rate))
                user_text = result_list[0].text.strip()
            except Exception as exc:
                self.log(f"语音识别失败：{exc}")
                continue

            if not user_text:
                self.log("识别结果为空，请再说一次。")
                continue

            self.log(f"你：{user_text}")
            if self.on_user_text:
                self.on_user_text(user_text)

            try:
                self.respond_to_text(user_text, speak=True, emit_user=False)
            except Exception as exc:
                self.log(f"Lumi 生成回复失败：{exc}")
                continue

        self.log("对话已停止。")

    def start(self) -> bool:
        with self._lock:
            if self.running:
                return True
            if not all([self.asr, self.llm, self.tts_ready]):
                self.log("请先加载模型。")
                return False
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            return True

    def stop(self) -> None:
        with self._lock:
            self.running = False
            thread = self.thread
        if thread and thread.is_alive():
            thread.join(timeout=2.0)
