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
    x: active ? 0 : 22

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on x { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

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
        y: 24
        text: appBridge.t("chat.title", root.language)
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.92
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeTitle : 32
        font.weight: Font.DemiBold
    }

    Text {
        x: 30
        y: 70
        width: parent.width * 0.58
        text: chatBridge && chatBridge.running ? appBridge.t("chat.status.listening", root.language) : (chatBridge && chatBridge.ready ? appBridge.t("chat.status.ready", root.language) : appBridge.t("chat.status.idle", root.language))
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.68
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        elide: Text.ElideRight
    }

    Flickable {
        id: scroll
        x: 28
        y: 118
        width: parent.width * 0.72
        height: parent.height - 230
        clip: true
        contentWidth: width
        contentHeight: column.height

        Column {
            id: column
            width: scroll.width
            spacing: 20
            Repeater {
                model: transcript
                PresenceText {
                    width: column.width
                    role: model.role
                    body: model.body
                    theme: root.theme
                }
            }
        }
    }

    Column {
        x: parent.width * 0.78
        y: 142
        width: parent.width * 0.19
        spacing: 12
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: chatBridge && chatBridge.running ? appBridge.t("chat.status.listening", root.language) : appBridge.t("chat.listen", root.language); subtitle: appBridge.t("chat.voice", root.language); width: parent.width; onActivated: chatBridge.startVoice() }
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("chat.stop", root.language); subtitle: appBridge.t("chat.voice.stop", root.language); width: parent.width; onActivated: chatBridge.stopVoice() }
        OrbitNodeButton { theme: root.theme; motion: root.motion; label: appBridge.t("chat.clear", root.language); subtitle: appBridge.t("chat.voice.clear", root.language); width: parent.width; onActivated: chatBridge.clear() }
    }

    SpatialInput {
        id: input
        x: 28
        y: parent.height - 82
        width: parent.width * 0.72
        theme: root.theme
        motion: root.motion
        placeholder: appBridge.t("chat.placeholder", root.language)
        onAccepted: {
            chatBridge.sendText(text)
            input.text = ""
        }
    }

    OrbitNodeButton {
        x: input.x + input.width + 18
        y: input.y - 18
        width: Math.min(190, parent.width - x - 12)
        height: 82
        theme: root.theme
        motion: root.motion
        label: appBridge.t("chat.send", root.language)
        subtitle: appBridge.t("chat.placeholder", root.language)
        onActivated: {
            chatBridge.sendText(input.text)
            input.text = ""
        }
    }
}
