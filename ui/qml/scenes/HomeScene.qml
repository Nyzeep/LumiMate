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

    function stateLabel() {
        return appBridge.t("state." + emotionBridge.mood, appBridge.language)
    }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 620
        numberLabel: appBridge.t("scene.home.title", appBridge.language)
        titleEn: "Home Space"
        subtitle: appBridge.t("scene.home.subtitle", appBridge.language)
    }

    Column {
        x: 0
        y: 124
        width: root.width * 0.28
        spacing: 18

        Text {
            text: appBridge.t("home.greeting.evening", appBridge.language)
            color: colors.neuralWhite
            font.family: typography.display(appBridge.language)
            font.pixelSize: typography.hero
        }

        Text {
            width: parent.width - 12
            text: appBridge.t("home.greeting.default", appBridge.language)
            wrapMode: Text.WordWrap
            lineHeight: 1.35
            color: colors.quietText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.body
        }

        GlassPanel {
            width: parent.width - 8
            height: 216

            Column {
                anchors.fill: parent
                spacing: 18

                MetricLine {
                    width: parent.width
                    label: appBridge.t("home.metric.state", appBridge.language)
                    value: root.stateLabel()
                    detail: chatBridge.status
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("home.metric.presence", appBridge.language)
                    value: root.percentText(emotionBridge.presenceLevel)
                    detail: appBridge.t("home.metric.presence.detail", appBridge.language)
                    progress: emotionBridge.presenceLevel
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("home.metric.breath", appBridge.language)
                    value: root.percentText(emotionBridge.breathLevel)
                    detail: appBridge.t("home.metric.breath.detail", appBridge.language)
                    progress: emotionBridge.breathLevel
                }
            }
        }

        GlassPanel {
            width: parent.width - 8
            height: 124
            tone: "strong"

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: appBridge.t("home.memory.title", appBridge.language)
                    color: colors.softAmber
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    width: parent.width
                    text: appBridge.t("home.memory.body", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    lineHeight: 1.4
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
            }
        }
    }

    Item {
        x: root.width * 0.33
        y: 84
        width: root.width * 0.58
        height: root.height * 0.66

        AmbientGlow {
            anchors.centerIn: parent
            width: parent.width * 0.64
            height: width
            glowColor: colors.nebulaGold
            glowOpacity: 0.24
        }

        Repeater {
            model: [0.26, 0.40, 0.56]

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                width: parent.width * modelData
                height: width * 0.72
                radius: width / 2
                color: "transparent"
                border.width: 1
                border.color: index === 0 ? Qt.rgba(0.95, 0.78, 0.63, 0.24) : Qt.rgba(0.62, 0.69, 0.82, 0.12)
            }
        }

        HeroCore {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.verticalCenterOffset: 30
            coreDiameter: 204
            symbol: "\u25B3"
            label: appBridge.t("home.cta.label", appBridge.language)
            subtitle: appBridge.t("home.cta.subtitle", appBridge.language)
            pulseLevel: emotionBridge.presenceLevel
            onActivated: appBridge.navigate("chat")
        }
    }

    Row {
        x: 0
        y: root.height - 118
        spacing: 14

        OrbitButton {
            width: 246
            label: appBridge.t("home.quick.chat", appBridge.language)
            subtitle: appBridge.t("home.quick.chat.sub", appBridge.language)
            tier: "primary"
            active: true
            symbol: "\u25B3"
            onActivated: appBridge.navigate("chat")
        }

        OrbitButton {
            width: 246
            label: appBridge.t("home.quick.companion", appBridge.language)
            subtitle: appBridge.t("home.quick.companion.sub", appBridge.language)
            tier: "secondary"
            symbol: "\u2726"
            onActivated: appBridge.navigate("companion")
        }

        OrbitButton {
            width: 246
            label: appBridge.t("home.quick.workbench", appBridge.language)
            subtitle: appBridge.t("home.quick.workbench.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25C8"
            onActivated: appBridge.navigate("workbench")
        }
    }
}
