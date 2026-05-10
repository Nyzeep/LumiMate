import QtQuick
import "../components"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property bool active: false
    visible: opacity > 0.01
    opacity: active ? 1 : 0
    scale: active ? 1 : 0.97

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

    Text {
        x: 28
        y: 22
        text: appBridge.t("workbench.title", root.language)
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.92
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeTitle : 32
        font.weight: Font.DemiBold
    }

    Text {
        x: 30
        y: 68
        width: Math.min(parent.width * 0.62, 640)
        text: appBridge.t("workbench.subtitle", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.66
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        wrapMode: Text.WordWrap
    }

    ModelRitualProgress {
        x: 24
        y: 104
        width: parent.width - 48
        theme: root.theme
        motion: root.motion
        language: root.language
    }

    Column {
        id: fields
        x: 28
        y: 326
        width: parent.width * 0.62
        spacing: 8
        SpatialInput { id: asrPath; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.asr", root.language); text: modelBridge ? modelBridge.defaultAsrPath : "" }
        SpatialInput { id: llmPath; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.llm", root.language); text: modelBridge ? modelBridge.defaultLlmPath : "" }
        SpatialInput { id: ttsDir; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.tts", root.language); text: modelBridge ? modelBridge.defaultTtsDir : "" }
        SpatialInput { id: refAudio; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.refAudio", root.language); text: modelBridge ? modelBridge.defaultRefAudio : "" }
        SpatialInput { id: refText; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.refText", root.language); text: modelBridge ? modelBridge.defaultRefText : "" }
        SpatialInput { id: roleName; width: parent.width; theme: root.theme; motion: root.motion; placeholder: appBridge.t("workbench.role", root.language); text: modelBridge ? modelBridge.defaultTtsCharacter : "" }
    }

    Column {
        x: parent.width * 0.72
        y: 320
        width: parent.width * 0.24
        spacing: 10
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("workbench.load", root.language); subtitle: appBridge.t("home.action.workbench.sub", root.language); width: parent.width; onActivated: modelBridge.loadModels(asrPath.text, llmPath.text, ttsDir.text, refAudio.text, refText.text, roleName.text, 100, 3, 0.005) }
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("workbench.switch", root.language); subtitle: appBridge.t("workbench.safeUnload", root.language); width: parent.width; onActivated: modelBridge.switchModels(asrPath.text, llmPath.text, ttsDir.text, refAudio.text, refText.text, roleName.text, 100, 3, 0.005) }
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("workbench.release", root.language); subtitle: appBridge.t("workbench.cacheVram", root.language); width: parent.width; onActivated: modelBridge.releaseCache() }
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("workbench.update", root.language); subtitle: appBridge.t("workbench.remoteSync", root.language); width: parent.width; onActivated: appBridge.checkUpdates() }
    }
}
