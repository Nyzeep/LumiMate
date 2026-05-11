import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string role: "assistant"
    property string author: role === "assistant" ? "Lumi" : "You"
    property string body: ""
    readonly property bool assistant: root.role === "assistant"

    width: parent ? parent.width : 400
    implicitHeight: bubbleColumn.implicitHeight + 8

    Column {
        id: bubbleColumn
        width: root.width * 0.74
        anchors.left: root.assistant ? parent.left : undefined
        anchors.right: root.assistant ? undefined : parent.right
        spacing: 8

        Row {
            visible: root.assistant
            spacing: 10

            HaloIconButton {
                diameter: 28
                symbol: "✦"
                active: true
                clickable: false
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                text: root.author
                color: colors.quietText
                font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
                font.pixelSize: typography.small
            }
        }

        GlassPanel {
            width: parent.width
            implicitHeight: bubbleText.paintedHeight + 34
            tone: root.assistant ? "soft" : "strong"
            glowOpacity: root.assistant ? 0.06 : 0.11
            fillColor: root.assistant ? Qt.rgba(0.07, 0.11, 0.19, 0.48) : Qt.rgba(0.10, 0.16, 0.28, 0.76)
            edgeColor: root.assistant ? Qt.rgba(0.95, 0.77, 0.62, 0.18) : Qt.rgba(0.82, 0.73, 0.90, 0.20)

            Text {
                id: bubbleText
                anchors.fill: parent
                anchors.margins: 16
                text: root.body
                wrapMode: Text.WordWrap
                color: colors.neuralWhite
                font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
                font.pixelSize: typography.body
                lineHeight: 1.35
            }
        }
    }
}
