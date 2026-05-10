import QtQuick

Item {
    id: root
    property string role: "assistant"
    property string body: ""
    property var theme

    width: parent ? parent.width : 640
    height: Math.max(42, message.implicitHeight + 22)

    Rectangle {
        width: role === "user" ? 7 : 12
        height: width
        radius: width / 2
        x: role === "user" ? parent.width - width - 4 : 4
        y: 10
        color: role === "user" ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
        opacity: 0.72
    }

    Text {
        id: message
        text: root.body
        width: parent.width * 0.76
        x: role === "user" ? parent.width - width - 26 : 26
        y: 4
        wrapMode: Text.WordWrap
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: role === "user" ? 0.76 : 0.92
        horizontalAlignment: role === "user" ? Text.AlignRight : Text.AlignLeft
        font.family: root.theme ? root.theme.fontFamily : "Segoe UI"
        font.pixelSize: role === "user" ? 15 : 17
        lineHeight: 1.22
    }
}
