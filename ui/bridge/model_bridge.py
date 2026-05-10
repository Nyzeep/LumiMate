from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from config import AssistantConfig


class ModelBridge(QObject):
    stateChanged = pyqtSignal()
    progressChanged = pyqtSignal()
    loadedChanged = pyqtSignal()
    logAdded = pyqtSignal(str)

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self._controller = controller
        self._state = "idle"
        self._state_message = "Waiting"
        self._progress_step = 0
        self._progress_total = 0
        self._progress_message = "Waiting"
        self._loaded = False
        self._defaults = AssistantConfig.defaults()

        controller.state_changed.connect(self._on_state_changed)
        controller.progress.connect(self._on_progress)
        controller.loaded.connect(self._on_loaded)
        controller.log.connect(self.logAdded.emit)

    @pyqtProperty(str, notify=stateChanged)
    def state(self) -> str:
        return self._state

    @pyqtProperty(str, notify=stateChanged)
    def stateMessage(self) -> str:
        return self._state_message

    @pyqtProperty(int, notify=progressChanged)
    def progressStep(self) -> int:
        return self._progress_step

    @pyqtProperty(int, notify=progressChanged)
    def progressTotal(self) -> int:
        return self._progress_total

    @pyqtProperty(str, notify=progressChanged)
    def progressMessage(self) -> str:
        return self._progress_message

    @pyqtProperty(bool, notify=loadedChanged)
    def loaded(self) -> bool:
        return self._loaded

    @pyqtProperty(str, constant=True)
    def defaultAsrPath(self) -> str:
        return self._defaults.asr_path

    @pyqtProperty(str, constant=True)
    def defaultLlmPath(self) -> str:
        return self._defaults.llm_path

    @pyqtProperty(str, constant=True)
    def defaultTtsDir(self) -> str:
        return self._defaults.tts_model_dir

    @pyqtProperty(str, constant=True)
    def defaultRefAudio(self) -> str:
        return self._defaults.ref_audio_path

    @pyqtProperty(str, constant=True)
    def defaultRefText(self) -> str:
        return self._defaults.ref_text

    @pyqtProperty(str, constant=True)
    def defaultTtsCharacter(self) -> str:
        return self._defaults.tts_character

    @pyqtSlot(str, str, str, str, str, str, int, int, float)
    def loadModels(
        self,
        asr_path: str,
        llm_path: str,
        tts_dir: str,
        ref_audio: str,
        ref_text: str,
        tts_character: str,
        max_tokens: int,
        chunk_sec: int,
        energy_threshold: float,
    ) -> None:
        self._controller.load_models(self._config(asr_path, llm_path, tts_dir, ref_audio, ref_text, tts_character, max_tokens, chunk_sec, energy_threshold))

    @pyqtSlot(str, str, str, str, str, str, int, int, float)
    def switchModels(
        self,
        asr_path: str,
        llm_path: str,
        tts_dir: str,
        ref_audio: str,
        ref_text: str,
        tts_character: str,
        max_tokens: int,
        chunk_sec: int,
        energy_threshold: float,
    ) -> None:
        self._controller.switch_models(self._config(asr_path, llm_path, tts_dir, ref_audio, ref_text, tts_character, max_tokens, chunk_sec, energy_threshold))

    @pyqtSlot()
    def releaseCache(self) -> None:
        self._controller.release_cache()

    def _config(
        self,
        asr_path: str,
        llm_path: str,
        tts_dir: str,
        ref_audio: str,
        ref_text: str,
        tts_character: str,
        max_tokens: int,
        chunk_sec: int,
        energy_threshold: float,
    ) -> AssistantConfig:
        return AssistantConfig(
            asr_path=asr_path.strip(),
            llm_path=llm_path.strip(),
            tts_model_dir=tts_dir.strip(),
            ref_audio_path=ref_audio.strip(),
            ref_text=ref_text.strip(),
            tts_character=tts_character.strip() or self._defaults.tts_character,
            max_new_tokens=max(16, int(max_tokens or 100)),
            chunk_sec=max(1, int(chunk_sec or 3)),
            energy_threshold=max(0.001, float(energy_threshold or 0.005)),
        )

    def _on_state_changed(self, state: str, message: str) -> None:
        self._state = state
        self._state_message = message
        self.stateChanged.emit()

    def _on_progress(self, step: int, total: int, message: str) -> None:
        self._progress_step = step
        self._progress_total = total
        self._progress_message = message
        self.progressChanged.emit()

    def _on_loaded(self, success: bool) -> None:
        self._loaded = success
        self.loadedChanged.emit()
