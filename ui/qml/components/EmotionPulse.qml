import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    property real level: emotionBridge ? emotionBridge.presenceLevel : 0.5
    property real breath: emotionBridge ? emotionBridge.breathLevel : 0.5

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(root.width, root.height) * (0.52 + root.level * 0.18)
        height: width
        radius: width / 2
        color: colors.nebulaGold
        opacity: 0.08 + root.level * 0.09
    }

    Repeater {
        model: 4
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(root.width, root.height) * (0.26 + index * 0.13 + root.breath * 0.05)
            height: width
            radius: width / 2
            color: "transparent"
            border.width: index === 0 ? 2 : 1
            border.color: index === 0 ? colors.softAmber : colors.line
            opacity: 0.34 - index * 0.06 + root.level * 0.12

            RotationAnimation on rotation {
                loops: Animation.Infinite
                running: root.visible
                from: 0
                to: 360
                duration: (appBridge && appBridge.reduceMotion ? 10000 : 24000) + index * 4200
            }
        }
    }
}
