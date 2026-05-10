import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    function basename(path) {
        if (!path) {
            return ""
        }
        var normalized = String(path).replace(/\\/g, "/")
        var parts = normalized.split("/")
        return parts.length ? parts[parts.length - 1] : normalized
    }

    Text {
        x: 28
        y: 76
        text: appBridge.t("workbench.title", appBridge.language)
        color: colors.neuralWhite
        font.family: typography.display(appBridge.language)
        font.pixelSize: typography.title
    }

    Text {
        x: 28
        y: 116
        width: root.width * 0.46
        text: appBridge.t("workbench.subtitle", appBridge.language)
        wrapMode: Text.WordWrap
        color: colors.dimText
        font.family: typography.sans(appBridge.language)
        font.pixelSize: typography.body
    }

    Item {
        x: 26
        y: 184
        width: root.width * 0.34
        height: root.height - 220

        NeuralLoader {
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.84
            height: parent.width * 0.84
        }

        GlassPanel {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 176

            Column {
                x: 20
                y: 18
                spacing: 10
                Text {
                    text: appBridge.t("workbench.runtime.title", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }
                Text {
                    text: appBridge.t("workbench.phase." + modelBridge.state, appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.title
                }
                Text {
                    width: parent.width - 12
                    text: modelBridge.stateMessage
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
                Rectangle {
                    width: parent.width - 24
                    height: 2
                    color: Qt.rgba(0.60, 0.69, 0.82, 0.14)
                    Rectangle {
                        width: parent.width * (modelBridge.progressTotal > 0 ? modelBridge.progressStep / modelBridge.progressTotal : (modelBridge.loaded ? 1 : 0))
                        height: parent.height
                        color: colors.nebulaGold
                    }
                }
            }
        }
    }

    Row {
        x: root.width * 0.40
        y: 176
        spacing: 18

        Column {
            width: root.width * 0.17
            spacing: 12
            Text {
                text: appBridge.t("workbench.asr", appBridge.language)
                color: colors.dimText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
            Repeater {
                model: modelBridge.asrModels
                OrbitNode {
                    width: parent.width
                    title: root.basename(modelData)
                    subtitle: modelData
                    selected: modelData === modelBridge.selectedAsr
                    onActivated: modelBridge.selectModel("asr", modelData)
                }
            }
        }

        Column {
            width: root.width * 0.17
            spacing: 12
            Text {
                text: appBridge.t("workbench.llm", appBridge.language)
                color: colors.dimText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
            Repeater {
                model: modelBridge.llmModels
                OrbitNode {
                    width: parent.width
                    title: root.basename(modelData)
                    subtitle: modelData
                    selected: modelData === modelBridge.selectedLlm
                    onActivated: modelBridge.selectModel("llm", modelData)
                }
            }
        }

        Column {
            width: root.width * 0.17
            spacing: 12
            Text {
                text: appBridge.t("workbench.tts", appBridge.language)
                color: colors.dimText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
            Repeater {
                model: modelBridge.ttsModels
                OrbitNode {
                    width: parent.width
                    title: root.basename(modelData)
                    subtitle: modelData
                    selected: modelData === modelBridge.selectedTts
                    onActivated: modelBridge.selectModel("tts", modelData)
                }
            }
        }
    }

    Column {
        x: root.width * 0.40
        y: root.height - 164
        spacing: 12

        Row {
            spacing: 12
            SpatialInput {
                width: root.width * 0.24
                placeholderText: appBridge.t("workbench.reference", appBridge.language)
                text: modelBridge.selectedRefAudio
                onEditingFinished: modelBridge.setReferenceAudio(text)
            }
            SpatialInput {
                width: root.width * 0.14
                placeholderText: appBridge.t("workbench.role", appBridge.language)
                text: modelBridge.selectedTtsCharacter
                onEditingFinished: modelBridge.setTtsCharacter(text)
            }
        }

        SpatialInput {
            width: root.width * 0.40
            placeholderText: appBridge.t("workbench.reference_text", appBridge.language)
            text: modelBridge.selectedRefText
            onEditingFinished: modelBridge.setReferenceText(text)
        }

        Row {
            spacing: 12
            OrbitButton {
                width: 180
                label: appBridge.t("workbench.scan", appBridge.language)
                subtitle: modelBridge.modelRoot
                tier: "tertiary"
                onActivated: modelBridge.scanModels()
            }
            OrbitButton {
                width: 180
                label: appBridge.t("workbench.load", appBridge.language)
                subtitle: appBridge.t("workbench.selection.title", appBridge.language)
                tier: "primary"
                active: modelBridge.loaded
                onActivated: modelBridge.loadSelectedModels()
            }
            OrbitButton {
                width: 180
                label: appBridge.t("workbench.switch", appBridge.language)
                subtitle: appBridge.t("workbench.runtime.title", appBridge.language)
                tier: "secondary"
                onActivated: modelBridge.switchSelectedModels()
            }
            OrbitButton {
                width: 180
                label: appBridge.t("workbench.release", appBridge.language)
                subtitle: appBridge.t("workbench.phase.releasing_cache", appBridge.language)
                tier: "tertiary"
                onActivated: modelBridge.releaseCache()
            }
        }
    }
}
