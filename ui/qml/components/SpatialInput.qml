import QtQuick
import QtQuick.Controls
import "../design_system"

TextField {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    placeholderTextColor: Qt.rgba(0.79, 0.84, 0.90, 0.36)
    color: colors.neuralWhite
    selectByMouse: true
    padding: 18
    font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
    font.pixelSize: typography.body
    background: Rectangle {
        radius: 22
        color: Qt.rgba(0.07, 0.11, 0.19, 0.72)
        border.width: 1
        border.color: Qt.rgba(0.60, 0.69, 0.82, 0.18)
    }
}
