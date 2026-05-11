import QtQuick
import QtQuick.Controls
import "../design_system"

TextField {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string leadingSymbol: "◌"
    placeholderTextColor: Qt.rgba(0.79, 0.84, 0.90, 0.36)
    color: colors.neuralWhite
    selectByMouse: true
    leftPadding: 64
    rightPadding: 18
    topPadding: 17
    bottomPadding: 17
    font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
    font.pixelSize: typography.body
    background: Item {
        GlassPanel {
            anchors.fill: parent
            tone: "soft"
            radius: 26
            glowOpacity: root.activeFocus ? 0.12 : 0.05
            fillColor: Qt.rgba(0.06, 0.10, 0.18, 0.72)
            edgeColor: root.activeFocus ? Qt.rgba(0.95, 0.78, 0.63, 0.28) : Qt.rgba(0.60, 0.69, 0.82, 0.18)
        }

        HaloIconButton {
            x: 12
            anchors.verticalCenter: parent.verticalCenter
            diameter: 34
            symbol: root.leadingSymbol
            active: root.activeFocus
            clickable: false
        }
    }
}
