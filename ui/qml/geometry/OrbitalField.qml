import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property real density: 1.0

    Repeater {
        model: 7
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(root.width, root.height) * (0.20 + index * 0.105) * root.density
            height: width * (0.58 + index * 0.035)
            radius: height / 2
            color: "transparent"
            border.width: index % 3 === 0 ? 1.25 : 1
            border.color: root.theme ? root.theme.line : "#C9D9E2"
            opacity: 0.025 + (6 - index) * 0.012
            transform: Rotation {
                origin.x: width / 2
                origin.y: height / 2
                angle: 18 + index * 9
            }
            RotationAnimation on rotation {
                from: 0
                to: 360
                duration: (root.motion ? root.motion.deepOrbitDuration : 52000) + index * 5300
                loops: Animation.Infinite
                running: true
            }
        }
    }

    Repeater {
        model: 16
        Rectangle {
            property real baseY: root.height * (0.15 + ((index * 23) % 70) / 100)
            property real drift: 10 + index % 8
            width: 2 + (index % 3)
            height: width
            radius: width / 2
            color: index % 4 === 0 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
            opacity: 0.18 + (index % 5) * 0.035
            x: root.width * (0.18 + ((index * 37) % 64) / 100)
            y: baseY
            SequentialAnimation on y {
                loops: Animation.Infinite
                NumberAnimation { to: baseY - drift; duration: 9000 + index * 370; easing.type: Easing.InOutSine }
                NumberAnimation { to: baseY + drift; duration: 9000 + index * 370; easing.type: Easing.InOutSine }
            }
        }
    }
}
