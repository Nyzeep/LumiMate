import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property real density: 1.0

    Repeater {
        model: Math.round(42 * root.density)
        Rectangle {
            property real baseX: root.width * (((index * 29) % 100) / 100)
            property real driftX: 18 + index % 11
            width: 1.4 + (index % 4) * 0.65
            height: width
            radius: width / 2
            color: index % 5 === 0 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
            opacity: 0.05 + (index % 7) * 0.018
            x: baseX
            y: root.height * (((index * 47) % 100) / 100)

            SequentialAnimation on opacity {
                loops: Animation.Infinite
                NumberAnimation { to: 0.16 + (index % 5) * 0.02; duration: 4200 + index * 85; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0.04 + (index % 3) * 0.016; duration: 4800 + index * 92; easing.type: Easing.InOutSine }
            }
            SequentialAnimation on x {
                loops: Animation.Infinite
                NumberAnimation { to: baseX + driftX; duration: 18000 + index * 210; easing.type: Easing.InOutSine }
                NumberAnimation { to: baseX - driftX; duration: 18000 + index * 210; easing.type: Easing.InOutSine }
            }
        }
    }
}
