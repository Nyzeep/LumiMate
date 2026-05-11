import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    property string label: ""
    property string value: ""
    property string detail: ""
    property real progress: -1
    property int valuePixelSize: typography.title

    implicitWidth: 220
    implicitHeight: column.implicitHeight

    Column {
        id: column
        width: root.width
        spacing: 8

        Text {
            text: root.label
            color: colors.dimText
            font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.small
        }

        Text {
            text: root.value
            color: colors.neuralWhite
            font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: root.valuePixelSize
        }

        Text {
            visible: root.detail.length > 0
            width: parent.width
            text: root.detail
            color: colors.quietText
            wrapMode: Text.WordWrap
            font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.small
            lineHeight: 1.3
        }

        Item {
            visible: root.progress >= 0
            width: parent.width
            height: 8

            Rectangle {
                anchors.fill: parent
                radius: height / 2
                color: Qt.rgba(0.78, 0.73, 0.84, 0.12)
            }

            Rectangle {
                width: parent.width * Math.max(0, Math.min(1, root.progress))
                height: parent.height
                radius: height / 2
                color: colors.nebulaGold
            }
        }
    }
}
