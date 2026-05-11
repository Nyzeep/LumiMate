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

    function progressRatio() {
        if (modelBridge.progressTotal > 0) {
            return modelBridge.progressStep / modelBridge.progressTotal
        }
        return modelBridge.loaded ? 1 : 0
    }

    function stateLabel() {
        return appBridge.t("state." + modelBridge.state, appBridge.language)
    }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 720
        numberLabel: appBridge.t("scene.workbench.title", appBridge.language)
        titleEn: "Workbench"
        subtitle: appBridge.t("scene.workbench.subtitle", appBridge.language)
    }

    Item {
        x: 0
        y: 122
        width: root.width * 0.26
        height: root.height * 0.68

        NeuralLoader {
            anchors.top: parent.top
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width * 0.90
            height: width
        }

        GlassPanel {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 248
            tone: "strong"

            Column {
                anchors.fill: parent
                spacing: 14

                MetricLine {
                    width: parent.width
                    label: appBridge.t("workbench.metric.runtime", appBridge.language)
                    value: root.stateLabel()
                    detail: modelBridge.stateMessage
                    progress: root.progressRatio()
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("workbench.metric.selection", appBridge.language)
                    value: root.basename(modelBridge.selectedLlm)
                    detail: root.basename(modelBridge.selectedAsr) + " / " + root.basename(modelBridge.selectedTts)
                }

                Column {
                    width: parent.width
                    spacing: 6

                    Text {
                        text: appBridge.t("workbench.metric.log", appBridge.language)
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }

                    Repeater {
                        model: modelBridge.runtimeLog

                        Text {
                            width: parent ? parent.width : 0
                            text: modelData
                            color: colors.quietText
                            elide: Text.ElideRight
                            font.family: typography.sans(appBridge.language)
                            font.pixelSize: typography.small
                        }
                    }
                }
            }
        }
    }

    Row {
        x: root.width * 0.30
        y: 122
        spacing: 16

        GlassPanel {
            width: root.width * 0.20
            height: root.height * 0.42

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: appBridge.t("workbench.models.asr", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    visible: modelBridge.asrModels.length === 0
                    width: parent.width
                    text: appBridge.t("workbench.models.empty", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Flickable {
                    visible: modelBridge.asrModels.length > 0
                    width: parent.width
                    height: parent.height - 44
                    clip: true
                    contentWidth: width
                    contentHeight: asrColumn.height

                    Column {
                        id: asrColumn
                        width: parent.width
                        spacing: 10

                        Repeater {
                            model: modelBridge.asrModels

                            OrbitNode {
                                width: asrColumn.width
                                title: root.basename(modelData)
                                subtitle: modelData
                                selected: modelData === modelBridge.selectedAsr
                                symbol: "\u25CE"
                                onActivated: modelBridge.selectModel("asr", modelData)
                            }
                        }
                    }
                }
            }
        }

        GlassPanel {
            width: root.width * 0.20
            height: root.height * 0.42

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: appBridge.t("workbench.models.llm", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    visible: modelBridge.llmModels.length === 0
                    width: parent.width
                    text: appBridge.t("workbench.models.empty", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Flickable {
                    visible: modelBridge.llmModels.length > 0
                    width: parent.width
                    height: parent.height - 44
                    clip: true
                    contentWidth: width
                    contentHeight: llmColumn.height

                    Column {
                        id: llmColumn
                        width: parent.width
                        spacing: 10

                        Repeater {
                            model: modelBridge.llmModels

                            OrbitNode {
                                width: llmColumn.width
                                title: root.basename(modelData)
                                subtitle: modelData
                                selected: modelData === modelBridge.selectedLlm
                                symbol: "\u25C8"
                                onActivated: modelBridge.selectModel("llm", modelData)
                            }
                        }
                    }
                }
            }
        }

        GlassPanel {
            width: root.width * 0.20
            height: root.height * 0.42

            Column {
                anchors.fill: parent
                spacing: 12

                Text {
                    text: appBridge.t("workbench.models.tts", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    visible: modelBridge.ttsModels.length === 0
                    width: parent.width
                    text: appBridge.t("workbench.models.empty", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Flickable {
                    visible: modelBridge.ttsModels.length > 0
                    width: parent.width
                    height: parent.height - 44
                    clip: true
                    contentWidth: width
                    contentHeight: ttsColumn.height

                    Column {
                        id: ttsColumn
                        width: parent.width
                        spacing: 10

                        Repeater {
                            model: modelBridge.ttsModels

                            OrbitNode {
                                width: ttsColumn.width
                                title: root.basename(modelData)
                                subtitle: modelData
                                selected: modelData === modelBridge.selectedTts
                                symbol: "\u2726"
                                onActivated: modelBridge.selectModel("tts", modelData)
                            }
                        }
                    }
                }
            }
        }
    }

    GlassPanel {
        x: root.width * 0.30
        y: root.height - 224
        width: root.width * 0.66
        height: 192
        tone: "soft"

        Row {
            spacing: 12

            SpatialInput {
                width: root.width * 0.26
                placeholderText: appBridge.t("workbench.selection.audio", appBridge.language)
                text: modelBridge.selectedRefAudio
                leadingSymbol: "\u25CE"
                onEditingFinished: modelBridge.setReferenceAudio(text)
            }

            SpatialInput {
                width: root.width * 0.14
                placeholderText: appBridge.t("workbench.selection.role", appBridge.language)
                text: modelBridge.selectedTtsCharacter
                leadingSymbol: "\u25C7"
                onEditingFinished: modelBridge.setTtsCharacter(text)
            }
        }

        SpatialInput {
            y: 74
            width: parent.width
            placeholderText: appBridge.t("workbench.selection.text", appBridge.language)
            text: modelBridge.selectedRefText
            leadingSymbol: "\u25A1"
            onEditingFinished: modelBridge.setReferenceText(text)
        }

        Row {
            y: 130
            spacing: 12

            OrbitButton {
                width: 148
                label: appBridge.t("workbench.action.scan", appBridge.language)
                subtitle: appBridge.t("workbench.action.scan.sub", appBridge.language)
                tier: "tertiary"
                symbol: "\u25CE"
                onActivated: modelBridge.scanModels()
            }

            OrbitButton {
                width: 148
                label: appBridge.t("workbench.action.load", appBridge.language)
                subtitle: appBridge.t("workbench.action.load.sub", appBridge.language)
                tier: "primary"
                active: modelBridge.loaded
                symbol: "\u25B3"
                onActivated: {
                    modelBridge.loadSelectedModels()
                    appBridge.navigate("loading")
                }
            }

            OrbitButton {
                width: 148
                label: appBridge.t("workbench.action.switch", appBridge.language)
                subtitle: appBridge.t("workbench.action.switch.sub", appBridge.language)
                tier: "secondary"
                symbol: "\u25C8"
                onActivated: {
                    modelBridge.switchSelectedModels()
                    appBridge.navigate("loading")
                }
            }

            OrbitButton {
                width: 148
                label: appBridge.t("workbench.action.release", appBridge.language)
                subtitle: appBridge.t("workbench.action.release.sub", appBridge.language)
                tier: "tertiary"
                symbol: "\u25CB"
                onActivated: modelBridge.releaseCache()
            }
        }
    }
}
