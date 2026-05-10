import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    Row {
        x: 26
        y: 76
        spacing: 52

        Column {
            width: root.width * 0.34
            spacing: 18

            Text {
                text: appBridge.t("home.greeting.evening", appBridge.language)
                color: colors.softAmber
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.hero
            }

            Text {
                width: parent.width
                text: appBridge.t("home.subtitle", appBridge.language)
                wrapMode: Text.WordWrap
                color: colors.quietText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }

            GlassPanel {
                width: parent.width
                height: 120

                Column {
                    x: 20
                    y: 18
                    spacing: 10
                    Text {
                        text: appBridge.t("home.status.label", appBridge.language)
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                    Text {
                        text: appBridge.t("emotion." + emotionBridge.mood, appBridge.language)
                        color: colors.neuralWhite
                        font.family: typography.display(appBridge.language)
                        font.pixelSize: typography.title
                    }
                    Text {
                        text: appBridge.t("home.emotion.label", appBridge.language) + " · " + appBridge.t("home.emotion.value", appBridge.language)
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                }
            }

            GlassPanel {
                width: parent.width
                height: 108
                Text {
                    x: 20
                    y: 20
                    width: parent.width - 40
                    text: appBridge.t("home.memory.title", appBridge.language) + "\n" + appBridge.t("home.memory.body", appBridge.language)
                    color: colors.quietText
                    lineHeight: 1.4
                    wrapMode: Text.WordWrap
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
            }

            Column {
                spacing: 12
                OrbitButton {
                    label: appBridge.t("home.quick.chat", appBridge.language)
                    subtitle: appBridge.t("home.quick.chat.sub", appBridge.language)
                    tier: "primary"
                    active: true
                    onActivated: appBridge.navigate("chat")
                }
                OrbitButton {
                    label: appBridge.t("home.quick.companion", appBridge.language)
                    subtitle: appBridge.t("home.quick.companion.sub", appBridge.language)
                    tier: "secondary"
                    onActivated: appBridge.navigate("companion")
                }
                OrbitButton {
                    label: appBridge.t("home.quick.workbench", appBridge.language)
                    subtitle: appBridge.t("home.quick.workbench.sub", appBridge.language)
                    tier: "tertiary"
                    onActivated: appBridge.navigate("workbench")
                }
            }
        }

        Item {
            width: root.width * 0.48
            height: root.height - 120

            EmotionPulse {
                anchors.centerIn: parent
                width: parent.width * 0.74
                height: width
            }

            Image {
                anchors.centerIn: parent
                width: parent.width * 0.86
                height: parent.height * 0.82
                fillMode: Image.PreserveAspectFit
                source: appBridge.assetUrl("homeStage")
                opacity: 0.62
            }

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                width: parent.width * 0.44
                height: 16
                radius: 8
                color: Qt.rgba(0.95, 0.77, 0.62, 0.12)
            }
        }
    }
}
