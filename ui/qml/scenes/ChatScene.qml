import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    ListModel { id: transcript }

    Connections {
        target: chatBridge
        function onMessageAdded(role, text) {
            transcript.append({ "role": role, "body": text })
            Qt.callLater(function() {
                scroll.contentY = Math.max(0, scroll.contentHeight - scroll.height)
            })
        }
        function onClearRequested() {
            transcript.clear()
        }
    }

    Text {
        x: 28
        y: 76
        text: appBridge.t("chat.title", appBridge.language)
        color: colors.neuralWhite
        font.family: typography.display(appBridge.language)
        font.pixelSize: typography.title
    }

    Text {
        x: 28
        y: 116
        width: root.width * 0.42
        text: appBridge.t("chat.subtitle", appBridge.language)
        color: colors.dimText
        wrapMode: Text.WordWrap
        font.family: typography.sans(appBridge.language)
        font.pixelSize: typography.body
    }

    Item {
        x: root.width * 0.34
        y: 110
        width: root.width * 0.34
        height: root.height * 0.54

        EmotionPulse {
            anchors.centerIn: parent
            width: parent.width * 0.9
            height: width
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 64
            text: appBridge.t("chat.center.label", appBridge.language)
            color: colors.dimText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.small
        }

        VoiceWave {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            width: parent.width * 0.7
            height: 60
        }
    }

    Flickable {
        id: scroll
        x: root.width * 0.66
        y: 86
        width: root.width * 0.30
        height: root.height * 0.60
        clip: true
        contentWidth: width
        contentHeight: chatColumn.height

        Column {
            id: chatColumn
            width: scroll.width
            spacing: 12
            Repeater {
                model: transcript
                MessageOrbit {
                    width: chatColumn.width
                    role: model.role
                    body: model.body
                }
            }
        }
    }

    Row {
        x: 28
        y: root.height - 110
        spacing: 12

        SpatialInput {
            id: input
            width: root.width * 0.58
            height: 58
            placeholderText: appBridge.t("chat.placeholder", appBridge.language)
            onAccepted: {
                chatBridge.sendText(text)
                text = ""
            }
        }

        OrbitButton {
            width: 150
            height: 58
            label: appBridge.t("chat.send", appBridge.language)
            subtitle: chatBridge.status
            tier: "primary"
            onActivated: {
                chatBridge.sendText(input.text)
                input.text = ""
            }
        }
    }

    Column {
        x: root.width * 0.66
        y: root.height - 180
        spacing: 10

        OrbitButton {
            width: root.width * 0.30
            label: appBridge.t("chat.listen", appBridge.language)
            subtitle: appBridge.t("chat.status.listening", appBridge.language)
            tier: "secondary"
            active: chatBridge.running
            onActivated: chatBridge.startVoice()
        }
        OrbitButton {
            width: root.width * 0.30
            label: appBridge.t("chat.stop", appBridge.language)
            subtitle: appBridge.t("chat.status.ready", appBridge.language)
            tier: "tertiary"
            onActivated: chatBridge.stopVoice()
        }
    }
}
