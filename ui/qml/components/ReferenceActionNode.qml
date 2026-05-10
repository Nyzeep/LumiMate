import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string title: ""
    property string subtitle: ""
    property string glyph: "△"
    property real hoverAmount: hitArea.containsMouse ? 1 : 0
    signal activated()

    width: 180
    height: 148

    Behavior on hoverAmount {
        NumberAnimation { duration: root.motion ? root.motion.hoverDuration : 780; easing.type: Easing.OutCubic }
    }

    Item {
        id: node
        width: 94
        height: 94
        anchors.horizontalCenter: parent.horizontalCenter
        y: 0
        scale: 1 + root.hoverAmount * 0.045

        Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: parent.height
            radius: width / 2
            color: root.theme ? root.theme.panel : "#101B31"
            opacity: 0.46
            border.width: 1
            border.color: Qt.rgba(0.79, 0.85, 0.89, 0.18 + root.hoverAmount * 0.20)
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.68
            height: parent.height * 0.68
            radius: width / 2
            color: "transparent"
            border.width: 1
            border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
            opacity: 0.16 + root.hoverAmount * 0.38
            RotationAnimation on rotation {
                from: 0
                to: 360
                duration: root.motion ? root.motion.slowOrbitDuration : 28000
                loops: Animation.Infinite
                running: true
            }
        }

        Text {
            anchors.centerIn: parent
            text: root.glyph
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.70 + root.hoverAmount * 0.20
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 33
        }

        Repeater {
            model: 5
            Rectangle {
                width: 3 + (index % 2)
                height: width
                radius: width / 2
                color: index === 4 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
                opacity: 0.15 + root.hoverAmount * 0.18
                x: node.width / 2 + Math.cos(index * 1.256 + node.rotation / 57.3) * node.width * 0.47 - width / 2
                y: node.height / 2 + Math.sin(index * 1.256 + node.rotation / 57.3) * node.height * 0.32 - height / 2
            }
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 104
        width: parent.width
        text: root.title
        horizontalAlignment: Text.AlignHCenter
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.82 + root.hoverAmount * 0.12
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: 20
        elide: Text.ElideRight
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 131
        width: parent.width
        text: root.subtitle
        horizontalAlignment: Text.AlignHCenter
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.50 + root.hoverAmount * 0.14
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: 12
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
