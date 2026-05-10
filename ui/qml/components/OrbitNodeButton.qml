import QtQuick

Item {
    id: root
    property string label: ""
    property string subtitle: ""
    property string symbol: "orbit"
    property var theme
    property var motion
    property real nodeSize: 70
    property real hoverAmount: hitArea.containsMouse ? 1.0 : 0.0
    signal activated()

    width: Math.max(168, nodeSize + 132)
    height: Math.max(92, nodeSize + 34)
    opacity: enabled ? 1.0 : 0.36

    Behavior on hoverAmount {
        NumberAnimation { duration: root.motion ? root.motion.hoverDuration : 780; easing.type: Easing.OutCubic }
    }

    Item {
        id: orbit
        width: root.nodeSize
        height: root.nodeSize
        anchors.left: parent.left
        anchors.leftMargin: 6
        anchors.verticalCenter: parent.verticalCenter
        scale: 1.0 + root.hoverAmount * 0.035

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 1.82
            height: parent.height * 1.82
            radius: width / 2
            color: root.theme ? root.theme.accent : "#D97855"
            opacity: 0.028 + root.hoverAmount * 0.036
        }

        Repeater {
            model: 3
            Rectangle {
                anchors.centerIn: parent
                width: orbit.width * (0.86 + index * 0.32)
                height: width * 0.66
                radius: height / 2
                color: "transparent"
                border.width: 1
                border.color: root.theme ? root.theme.line : "#C9D9E2"
                opacity: 0.16 + root.hoverAmount * 0.19 - index * 0.035
                transform: Rotation {
                    origin.x: width / 2
                    origin.y: height / 2
                    angle: orbit.rotation + index * 28
                }
            }
        }

        Rectangle {
            id: core
            anchors.centerIn: parent
            width: orbit.width * (0.14 + root.hoverAmount * 0.025)
            height: width
            radius: width / 2
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.72 + root.hoverAmount * 0.18
        }

        Rectangle {
            width: 7
            height: 7
            radius: 4
            color: root.theme ? root.theme.accentSoft : "#F1A47A"
            opacity: 0.78 + root.hoverAmount * 0.18
            x: orbit.width / 2 + Math.cos(orbit.rotation * Math.PI / 180) * orbit.width * 0.48 - width / 2
            y: orbit.height / 2 + Math.sin(orbit.rotation * Math.PI / 180) * orbit.height * 0.32 - height / 2
        }

        NumberAnimation on rotation {
            from: 0
            to: 360
            duration: root.motion ? root.motion.slowOrbitDuration : 28000
            loops: Animation.Infinite
            running: true
        }
    }

    Rectangle {
        x: orbit.x + root.nodeSize * 0.92
        y: parent.height / 2
        width: Math.max(18, parent.width - x - 20)
        height: 1
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.16 + root.hoverAmount * 0.18
    }

    Text {
        id: title
        text: root.label
        x: orbit.x + root.nodeSize + 46
        y: parent.height / 2 - (root.subtitle ? 24 : 12)
        width: parent.width - x - 4
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.72 + root.hoverAmount * 0.24
        font.family: root.theme ? root.theme.fontFamily : "Segoe UI"
        font.pixelSize: 15
        font.weight: Font.DemiBold
        elide: Text.ElideRight
    }

    Text {
        text: root.subtitle
        visible: root.subtitle.length > 0
        x: title.x
        y: parent.height / 2 + 3
        width: parent.width - x - 4
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.58 + root.hoverAmount * 0.18
        font.family: root.theme ? root.theme.fontFamily : "Segoe UI"
        font.pixelSize: 11
        elide: Text.ElideRight
    }

    Rectangle {
        id: ripple
        anchors.centerIn: orbit
        width: 10
        height: 10
        radius: width / 2
        color: "transparent"
        border.width: 1
        border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
        opacity: 0
    }

    MouseArea {
        id: hitArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: {
            ripple.width = 10
            ripple.height = 10
            ripple.opacity = 0.62
            ripplePulse.restart()
            root.activated()
        }
    }

    ParallelAnimation {
        id: ripplePulse
        NumberAnimation { target: ripple; property: "width"; to: root.nodeSize * 1.75; duration: 920; easing.type: Easing.OutCubic }
        NumberAnimation { target: ripple; property: "height"; to: root.nodeSize * 1.75; duration: 920; easing.type: Easing.OutCubic }
        NumberAnimation { target: ripple; property: "opacity"; to: 0; duration: 920; easing.type: Easing.OutCubic }
    }
}
