import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    property real activity: chatBridge && chatBridge.running ? 1.0 : 0.25

    Repeater {
        model: 28
        Rectangle {
            property real baseHeight: 10 + (index % 7) * 4 + root.activity * 16
            width: 2
            radius: 1
            height: baseHeight
            x: index * 8
            anchors.verticalCenter: parent.verticalCenter
            color: index % 2 === 0 ? colors.softAmber : colors.line
            opacity: 0.18 + root.activity * 0.36

            SequentialAnimation on height {
                loops: Animation.Infinite
                running: root.visible
                NumberAnimation { to: 10 + ((index + 3) % 7) * 5 + root.activity * 24; duration: 1100 + (index % 6) * 120; easing.type: Easing.InOutSine }
                NumberAnimation { to: baseHeight; duration: 1100 + (index % 6) * 120; easing.type: Easing.InOutSine }
            }
        }
    }
}
