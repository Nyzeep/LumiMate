import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string label: ""
    property string glyph: "△"
    property bool checked: false
    property bool compact: false
    property real hoverAmount: (hitArea.containsMouse || checked) ? 1 : 0
    signal activated()

    width: 104
    height: compact ? 76 : 92

    Behavior on hoverAmount {
        NumberAnimation { duration: root.motion ? root.motion.hoverDuration : 780; easing.type: Easing.OutCubic }
    }

    Item {
        id: orbit
        width: compact ? 50 : 58
        height: width
        anchors.horizontalCenter: parent.horizontalCenter
        y: compact ? 2 : 4
        scale: 1 + root.hoverAmount * 0.045

        Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: parent.height
            radius: width / 2
            color: root.theme ? root.theme.accent : "#D97855"
            opacity: 0.035 + root.hoverAmount * 0.055
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.88
            height: parent.height * 0.88
            radius: width / 2
            color: "transparent"
            border.width: 1
            border.color: root.theme ? root.theme.line : "#C9D9E2"
            opacity: 0.22 + root.hoverAmount * 0.30
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.62
            height: parent.height * 0.62
            radius: width / 2
            color: "transparent"
            border.width: 1
            border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
            opacity: 0.16 + root.hoverAmount * 0.42
            RotationAnimation on rotation {
                from: 0
                to: 360
                duration: root.motion ? root.motion.slowOrbitDuration : 28000
                loops: Animation.Infinite
                running: root.checked || hitArea.containsMouse
            }
        }

        Text {
            anchors.centerIn: parent
            text: root.glyph
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.70 + root.hoverAmount * 0.22
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 25
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.compact ? 58 : 70
        text: root.label
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.54 + root.hoverAmount * 0.36
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.compact ? 12 : (root.theme ? root.theme.typeNav : 13)
    }

    MouseArea {
        id: hitArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: root.activated()
    }
}
