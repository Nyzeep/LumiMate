import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string title: ""
    property string subtitle: ""
    property bool selected: false
    property bool activeGlow: false
    signal activated()

    width: 220
    height: 96

    Rectangle {
        anchors.fill: parent
        radius: 24
        color: root.selected ? Qt.rgba(0.10, 0.17, 0.28, 0.88) : Qt.rgba(0.07, 0.11, 0.19, 0.60)
        border.width: 1
        border.color: root.selected ? Qt.rgba(0.95, 0.78, 0.62, 0.46) : Qt.rgba(0.60, 0.69, 0.82, 0.16)
    }

    Item {
        x: 14
        y: 14
        width: 68
        height: 68

        Repeater {
            model: 3
            Rectangle {
                anchors.centerIn: parent
                width: 24 + index * 16
                height: width
                radius: width / 2
                color: "transparent"
                border.width: 1
                border.color: index === 0 ? colors.softAmber : colors.line
                opacity: root.selected ? 0.52 - index * 0.08 : 0.26 - index * 0.05
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: 14
            height: 14
            radius: 7
            color: root.selected || root.activeGlow ? colors.nebulaGold : colors.line
            opacity: 0.88
        }
    }

    Text {
        x: 94
        y: 22
        width: parent.width - x - 12
        text: root.title
        color: colors.neuralWhite
        font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.section
        elide: Text.ElideMiddle
    }

    Text {
        x: 94
        y: 50
        width: parent.width - x - 12
        text: root.subtitle
        color: colors.dimText
        font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.small
        elide: Text.ElideMiddle
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.activated()
    }
}
