import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    property string symbol: "•"
    property bool active: false
    property bool clickable: true
    property int diameter: 34
    property color accentColor: colors.nebulaGold
    signal activated()

    width: diameter
    height: diameter
    readonly property real hoverAmount: mouse.containsMouse ? 1 : 0

    AmbientGlow {
        anchors.centerIn: parent
        width: parent.width * 1.8
        height: width
        glowColor: root.accentColor
        glowOpacity: root.active ? 0.22 : 0.06 + root.hoverAmount * 0.10
    }

    Rectangle {
        anchors.fill: parent
        radius: width / 2
        color: root.active ? Qt.rgba(0.16, 0.13, 0.18, 0.72) : Qt.rgba(0.08, 0.12, 0.20, 0.44)
        border.width: 1
        border.color: root.active ? Qt.rgba(0.95, 0.78, 0.63, 0.44) : Qt.rgba(0.64, 0.57, 0.68, 0.20)
    }

    Text {
        anchors.centerIn: parent
        text: root.symbol
        color: root.active ? colors.softAmber : colors.quietText
        font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: Math.max(14, root.diameter * 0.34)
    }

    MouseArea {
        id: mouse
        anchors.fill: parent
        enabled: root.clickable
        hoverEnabled: root.clickable
        cursorShape: root.clickable ? Qt.PointingHandCursor : Qt.ArrowCursor
        onClicked: root.activated()
    }
}
