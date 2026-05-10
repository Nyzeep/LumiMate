import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    property real progress: modelBridge && modelBridge.progressTotal > 0 ? modelBridge.progressStep / modelBridge.progressTotal : (modelBridge && modelBridge.loaded ? 1 : 0)
    property string phase: modelBridge ? modelBridge.state : "idle"

    Item {
        anchors.centerIn: parent
        width: Math.min(root.width, root.height) * 0.8
        height: width

        Repeater {
            model: 5
            Rectangle {
                anchors.centerIn: parent
                width: parent.width * (0.22 + index * 0.13)
                height: width
                radius: width / 2
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0 ? colors.nebulaGold : colors.line
                opacity: 0.18 + root.progress * 0.22 - index * 0.02
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * (0.08 + root.progress * 0.06)
            height: width
            radius: width / 2
            color: colors.nebulaGold
            opacity: 0.86
        }

        Repeater {
            model: 12
            Rectangle {
                width: 4
                height: 4
                radius: 2
                color: colors.softAmber
                x: parent.width / 2 + Math.cos(index / 12 * Math.PI * 2) * parent.width * (0.18 + root.progress * 0.16) - width / 2
                y: parent.height / 2 + Math.sin(index / 12 * Math.PI * 2) * parent.height * (0.18 + root.progress * 0.16) - height / 2
                opacity: 0.28 + root.progress * 0.62
            }
        }
    }
}
