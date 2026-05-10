import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string role: "assistant"
    property string body: ""

    width: parent ? parent.width : 400
    height: Math.max(72, textItem.paintedHeight + 28)

    Rectangle {
        anchors.fill: parent
        radius: 22
        color: root.role === "user" ? Qt.rgba(0.10, 0.18, 0.30, 0.74) : Qt.rgba(0.09, 0.13, 0.22, 0.58)
        border.width: 1
        border.color: root.role === "user" ? Qt.rgba(0.60, 0.74, 0.92, 0.28) : Qt.rgba(0.95, 0.77, 0.62, 0.18)
    }

    Text {
        id: textItem
        x: 18
        y: 14
        width: parent.width - 36
        text: root.body
        wrapMode: Text.WordWrap
        color: colors.neuralWhite
        font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.body
    }
}
