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
    property string symbol: "◈"
    signal activated()

    width: 220
    height: 102

    GlassPanel {
        anchors.fill: parent
        tone: root.selected ? "strong" : "soft"
        glowOpacity: root.selected ? 0.14 : 0.05
        edgeColor: root.selected ? Qt.rgba(0.95, 0.78, 0.62, 0.36) : Qt.rgba(0.60, 0.69, 0.82, 0.14)
        fillColor: root.selected ? Qt.rgba(0.09, 0.16, 0.28, 0.82) : Qt.rgba(0.06, 0.10, 0.18, 0.58)
    }

    HaloIconButton {
        x: 16
        y: 18
        diameter: 48
        symbol: root.symbol
        active: root.selected || root.activeGlow
        clickable: false
    }

    Text {
        x: 82
        y: 18
        width: parent.width - x - 12
        text: root.title
        color: colors.neuralWhite
        font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.section
        elide: Text.ElideMiddle
    }

    Text {
        x: 82
        y: 46
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
