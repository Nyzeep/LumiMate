import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Motion { id: motion }
    property int particleCount: 42
    property color particleColor: colors.softAmber
    property real intensity: 0.45

    Repeater {
        model: root.particleCount
        Rectangle {
            property real baseY: (root.height - height) * (((index * 61) % 100) / 100)
            width: 2 + (index % 3)
            height: width
            radius: width / 2
            x: (root.width - width) * (((index * 37) % 100) / 100)
            y: baseY
            color: root.particleColor
            opacity: 0.08 + ((index % 5) * 0.03) + root.intensity * 0.18

            SequentialAnimation on y {
                loops: Animation.Infinite
                running: root.visible
                NumberAnimation { to: baseY - 18 - (index % 7) * 2; duration: (12000 + (index % 9) * 1800) * motion.factor; easing.type: Easing.InOutSine }
                NumberAnimation { to: baseY; duration: (12000 + (index % 9) * 1800) * motion.factor; easing.type: Easing.InOutSine }
            }
        }
    }
}
