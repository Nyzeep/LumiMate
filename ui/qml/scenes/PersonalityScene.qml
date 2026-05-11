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

    function basename(path) {
        if (!path) {
            return ""
        }
        var normalized = String(path).replace(/\\/g, "/")
        var parts = normalized.split("/")
        return parts.length ? parts[parts.length - 1] : normalized
    }

    function moodLabel() {
        return appBridge.t("state." + emotionBridge.mood, appBridge.language)
    }

    function stageLabel() {
        return appBridge.t("state." + companionBridge.stageMode, appBridge.language)
    }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 680
        numberLabel: appBridge.t("scene.personality.title", appBridge.language)
        titleEn: "Personality"
        subtitle: appBridge.t("scene.personality.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 122
        width: root.width * 0.24
        height: root.height * 0.58

        Column {
            anchors.fill: parent
            spacing: 16

            MetricLine {
                width: parent.width
                label: appBridge.t("personality.metric.mood", appBridge.language)
                value: root.moodLabel()
                detail: root.stageLabel()
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("personality.metric.voice", appBridge.language)
                value: modelBridge.selectedTtsCharacter
                detail: root.basename(modelBridge.selectedTts)
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("personality.metric.presence", appBridge.language)
                value: root.percentText(emotionBridge.presenceLevel)
                detail: appBridge.t("personality.metric.presence.detail", appBridge.language)
                progress: emotionBridge.presenceLevel
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("personality.metric.breath", appBridge.language)
                value: root.percentText(emotionBridge.breathLevel)
                detail: appBridge.t("personality.metric.breath.detail", appBridge.language)
                progress: emotionBridge.breathLevel
            }
        }
    }

    Item {
        x: root.width * 0.30
        y: 98
        width: root.width * 0.35
        height: root.height * 0.66

        HeroCore {
            anchors.centerIn: parent
            coreDiameter: 224
            symbol: "\u25B3"
            label: appBridge.t("personality.center.label", appBridge.language)
            subtitle: appBridge.t("personality.center.subtitle", appBridge.language)
            pulseLevel: emotionBridge.presenceLevel
            active: true
            onActivated: appBridge.navigate("chat")
        }
    }

    Column {
        x: root.width * 0.70
        y: 122
        spacing: 18

        GlassPanel {
            width: root.width * 0.24
            height: 204
            tone: "strong"

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: appBridge.t("personality.panel.profile", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    text: appBridge.t("personality.panel.profile.voice", appBridge.language) + ": " + modelBridge.selectedTtsCharacter
                    color: colors.quietText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }

                Text {
                    text: appBridge.t("personality.panel.profile.stage", appBridge.language) + ": " + root.stageLabel()
                    color: colors.quietText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }

                Text {
                    text: appBridge.t("personality.panel.profile.startup", appBridge.language) + ": " + appBridge.t("nav." + appBridge.startupPage, appBridge.language)
                    width: parent.width
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
            }
        }

        GlassPanel {
            width: root.width * 0.24
            height: 162

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: appBridge.t("personality.panel.dialogue", appBridge.language)
                    color: colors.softAmber
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    text: appBridge.t("personality.panel.dialogue.count", appBridge.language) + ": " + chatBridge.messageCount
                    color: colors.quietText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }

                Text {
                    width: parent.width
                    text: chatBridge.status
                    wrapMode: Text.WordWrap
                    color: colors.dimText
                    lineHeight: 1.35
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
            }
        }
    }

    Row {
        x: root.width * 0.30
        y: root.height - 112
        spacing: 14

        OrbitButton {
            width: 196
            label: appBridge.t("personality.action.chat", appBridge.language)
            subtitle: appBridge.t("personality.action.chat.sub", appBridge.language)
            tier: "primary"
            symbol: "\u25B3"
            onActivated: appBridge.navigate("chat")
        }

        OrbitButton {
            width: 196
            label: appBridge.t("personality.action.companion", appBridge.language)
            subtitle: appBridge.t("personality.action.companion.sub", appBridge.language)
            tier: "secondary"
            symbol: "\u2726"
            onActivated: appBridge.navigate("companion")
        }

        OrbitButton {
            width: 196
            label: appBridge.t("personality.action.settings", appBridge.language)
            subtitle: appBridge.t("personality.action.settings.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u2318"
            onActivated: appBridge.navigate("settings")
        }
    }
}
