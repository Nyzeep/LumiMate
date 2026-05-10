import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string label: ""
    property string subtitle: ""
    property string tier: "primary"
    property bool active: false
    signal activated()

    width: 230
    height: tier === "primary" ? 86 : 74

    readonly property real hoverAmount: hitArea.containsMouse ? 1 : 0

    Rectangle {
        anchors.fill: parent
        radius: 30
        color: root.tier === "primary"
            ? Qt.rgba(0.09, 0.14, 0.24, 0.88)
            : root.tier === "secondary"
                ? Qt.rgba(0.08, 0.13, 0.22, 0.74)
                : Qt.rgba(0.07, 0.11, 0.18, 0.46)
        border.width: 1
        border.color: root.active || root.hoverAmount > 0
            ? Qt.rgba(0.96, 0.78, 0.63, 0.44)
            : Qt.rgba(0.60, 0.69, 0.82, 0.18)
    }

    AmbientGlow {
        anchors.centerIn: parent
        width: parent.width * 0.74
        height: width
        glowColor: colors.amber
        glowOpacity: root.tier === "primary" ? 0.10 + root.hoverAmount * 0.10 : 0.05 + root.hoverAmount * 0.05
    }

    Rectangle {
        x: 18
        y: parent.height / 2 - 20
        width: 40
        height: 40
        radius: 20
        color: Qt.rgba(0.95, 0.77, 0.62, 0.10)
        border.width: 1
        border.color: Qt.rgba(0.95, 0.77, 0.62, 0.24)
    }

    Text {
        x: 72
        y: 22
        text: root.label
        color: colors.neuralWhite
        font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.section
    }

    Text {
        x: 72
        y: 48
        width: parent.width - x - 16
        text: root.subtitle
        color: colors.dimText
        font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.small
        elide: Text.ElideRight
    }

    MouseArea {
        id: hitArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.activated()
    }
}
