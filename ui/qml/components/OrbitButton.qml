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
    property string symbol: "✦"
    signal activated()

    width: 246
    height: tier === "primary" ? 88 : 78

    readonly property real hoverAmount: hitArea.containsMouse ? 1 : 0

    GlassPanel {
        anchors.fill: parent
        tone: root.tier === "primary" ? "strong" : "soft"
        glowOpacity: root.active ? 0.16 : (root.tier === "primary" ? 0.12 : 0.06) + root.hoverAmount * 0.06
        fillColor: root.tier === "primary"
            ? Qt.rgba(0.09, 0.14, 0.24, 0.84)
            : root.tier === "secondary"
                ? Qt.rgba(0.08, 0.12, 0.22, 0.72)
                : Qt.rgba(0.06, 0.10, 0.18, 0.48)
        edgeColor: root.active || root.hoverAmount > 0
            ? Qt.rgba(0.96, 0.78, 0.63, 0.40)
            : Qt.rgba(0.64, 0.57, 0.68, 0.18)
    }

    HaloIconButton {
        x: 14
        anchors.verticalCenter: parent.verticalCenter
        diameter: 44
        symbol: root.symbol
        active: root.active || root.hoverAmount > 0
        clickable: false
    }

    Text {
        x: 72
        y: 18
        text: root.label
        color: colors.neuralWhite
        font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
        font.pixelSize: typography.section
    }

    Text {
        x: 72
        y: 45
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
