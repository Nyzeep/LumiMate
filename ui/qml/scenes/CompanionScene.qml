import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    function percentText(value) {
        return Math.round(Math.max(0, Math.min(1, value)) * 100) + "%"
    }

    function stageLabel() {
        return appBridge.t("state." + companionBridge.stageMode, appBridge.language)
    }

    function memoryDensity() {
        return Math.min(0.96, 0.28 + chatBridge.messageCount * 0.04)
    }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 660
        numberLabel: appBridge.t("scene.companion.title", appBridge.language)
        titleEn: "Companion Space"
        subtitle: appBridge.t("scene.companion.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 126
        width: root.width * 0.25
        height: root.height * 0.56

        Column {
            anchors.fill: parent
            spacing: 18

            MetricLine {
                width: parent.width
                label: appBridge.t("companion.metric.stage", appBridge.language)
                value: root.stageLabel()
                detail: chatBridge.status
                progress: emotionBridge.presenceLevel
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("companion.metric.voice", appBridge.language)
                value: root.percentText(companionBridge.speechLevel)
                detail: appBridge.t("companion.metric.voice.detail", appBridge.language)
                progress: companionBridge.speechLevel
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("companion.metric.renderer", appBridge.language)
                value: companionBridge.rendererType
                detail: companionBridge.rendererCapability
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("companion.metric.memory", appBridge.language)
                value: root.percentText(root.memoryDensity())
                detail: appBridge.t("companion.metric.memory.detail", appBridge.language)
                progress: root.memoryDensity()
            }
        }
    }

    Item {
        x: root.width * 0.31
        y: 72
        width: root.width * 0.63
        height: root.height * 0.72

        AmbientGlow {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenterOffset: parent.width * 0.18
            anchors.verticalCenterOffset: -6
            width: parent.width * 0.58
            height: width
            glowColor: colors.softAmber
            glowOpacity: 0.18 + companionBridge.speechLevel * 0.14
        }

        Repeater {
            model: 6

            Rectangle {
                width: parent.width * (0.18 + index * 0.10)
                height: width
                radius: width / 2
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenterOffset: parent.width * 0.18
                anchors.verticalCenterOffset: -8
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0
                    ? Qt.rgba(0.95, 0.78, 0.63, 0.36)
                    : Qt.rgba(0.68, 0.69, 0.82, 0.10)
                opacity: 0.90 - index * 0.10
            }
        }

        Repeater {
            model: [0.20, 0.44, 0.72]

            Rectangle {
                x: parent.width * (0.44 + modelData * 0.2)
                y: parent.height * (0.28 + index * 0.18)
                width: index === 0 ? 8 : 5
                height: width
                radius: width / 2
                color: colors.softAmber
                opacity: 0.84
            }
        }
    }

    Row {
        x: root.width * 0.37
        y: root.height - 110
        spacing: 26

        Repeater {
            model: [
                { labelKey: "companion.action.chat", symbol: "\u25B3", target: "chat" },
                { labelKey: "companion.action.personality", symbol: "\u25C7", target: "personality" },
                { labelKey: "companion.action.workbench", symbol: "\u25C8", target: "workbench" },
                { labelKey: "companion.action.about", symbol: "\u2609", target: "about" }
            ]

            Item {
                width: 112
                height: 72

                HaloIconButton {
                    anchors.horizontalCenter: parent.horizontalCenter
                    diameter: 42
                    symbol: modelData.symbol
                    active: appBridge.currentPage === modelData.target
                    onActivated: appBridge.navigate(modelData.target)
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 50
                    width: 112
                    text: appBridge.t(modelData.labelKey, appBridge.language)
                    color: colors.quietText
                    horizontalAlignment: Text.AlignHCenter
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }
            }
        }
    }
}
