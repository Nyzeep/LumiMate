import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

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
        widthHint: 660
        numberLabel: appBridge.t("scene.loading.title", appBridge.language)
        titleEn: "Loading Space"
        subtitle: appBridge.t("scene.loading.subtitle", appBridge.language)
    }

    Item {
        x: 0
        y: 120
        width: root.width * 0.54
        height: root.height * 0.50

        NeuralLoader {
            anchors.centerIn: parent
            width: parent.width * 0.58
            height: width
        }

        Column {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 8
            spacing: 6

            Text {
                text: root.stateLabel()
                color: colors.neuralWhite
                horizontalAlignment: Text.AlignHCenter
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.title
            }

            Text {
                width: 360
                text: modelBridge.stateMessage
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                color: colors.dimText
                lineHeight: 1.35
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }
        }
    }

    GlassPanel {
        x: root.width * 0.60
        y: 120
        width: root.width * 0.34
        height: root.height * 0.50

        Column {
            anchors.fill: parent
            spacing: 14

            MetricLine {
                width: parent.width
                label: appBridge.t("loading.metric.progress", appBridge.language)
                value: Math.round(root.progressRatio() * 100) + "%"
                detail: appBridge.t("loading.metric.progress.detail", appBridge.language)
                progress: root.progressRatio()
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("loading.metric.current", appBridge.language)
                value: root.stateLabel()
                detail: modelBridge.progressMessage
            }

            Repeater {
                model: modelBridge.loadingSteps

                Row {
                    width: parent ? parent.width : 0
                    spacing: 12

                    HaloIconButton {
                        diameter: 30
                        clickable: false
                        active: modelData.done || modelData.active
                        symbol: modelData.done ? "\u2713" : modelData.active ? "\u25CE" : "\u25CB"
                    }

                    Column {
                        spacing: 4

                        Text {
                            text: appBridge.t(modelData.labelKey, appBridge.language)
                            color: colors.neuralWhite
                            font.family: typography.display(appBridge.language)
                            font.pixelSize: typography.section
                        }

                        Text {
                            text: modelData.done
                                ? appBridge.t("common.done", appBridge.language)
                                : modelData.active
                                    ? appBridge.t("common.active", appBridge.language)
                                    : appBridge.t("common.pending", appBridge.language)
                            color: modelData.done ? colors.success : modelData.active ? colors.softAmber : colors.dimText
                            font.family: typography.sans(appBridge.language)
                            font.pixelSize: typography.small
                        }
                    }
                }
            }
        }
    }

    GlassPanel {
        x: 0
        y: root.height - 170
        width: root.width * 0.54
        height: 138
        tone: "strong"

        Column {
            anchors.fill: parent
            spacing: 8

            Text {
                text: appBridge.t("loading.log.title", appBridge.language)
                color: colors.softAmber
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.section
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

    Row {
        x: root.width * 0.60
        y: root.height - 150
        spacing: 12

        OrbitButton {
            width: 172
            label: appBridge.t("loading.action.workbench", appBridge.language)
            subtitle: appBridge.t("loading.action.workbench.sub", appBridge.language)
            tier: "secondary"
            symbol: "\u25C8"
            onActivated: appBridge.navigate("workbench")
        }

        OrbitButton {
            width: 172
            label: appBridge.t("loading.action.scan", appBridge.language)
            subtitle: appBridge.t("loading.action.scan.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25CE"
            onActivated: modelBridge.scanModels()
        }

        OrbitButton {
            width: 172
            label: appBridge.t("loading.action.release", appBridge.language)
            subtitle: appBridge.t("loading.action.release.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25CB"
            onActivated: modelBridge.releaseCache()
        }
    }
}
