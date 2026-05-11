import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    Motion { id: motion }

    property string symbol: "△"
    property string label: ""
    property string subtitle: ""
    property real pulseLevel: emotionBridge ? emotionBridge.presenceLevel : 0.5
    property bool active: true
    property real coreDiameter: 178
    signal activated()

    width: Math.max(coreDiameter + 60, 260)
    height: coreDiameter + (label.length > 0 ? 118 : 24)
    property real orbitAngle: 0

    NumberAnimation on orbitAngle {
        from: 0
        to: 360
        duration: motion.orbitDuration
        loops: Animation.Infinite
        running: root.visible && !appBridge.reduceMotion
    }

    Item {
        id: core
        anchors.horizontalCenter: parent.horizontalCenter
        y: 6
        width: root.coreDiameter
        height: root.coreDiameter

        AmbientGlow {
            anchors.centerIn: parent
            width: parent.width * 1.9
            height: width
            glowColor: colors.nebulaGold
            glowOpacity: root.active ? 0.26 : 0.12
        }

        Repeater {
            model: 5
            Rectangle {
                anchors.centerIn: parent
                width: parent.width * (0.34 + index * 0.15)
                height: width
                radius: width / 2
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0 ? Qt.rgba(0.95, 0.77, 0.62, 0.48) : Qt.rgba(0.73, 0.65, 0.78, 0.18)
                opacity: 0.72 - index * 0.10
            }
        }

        Repeater {
            model: 4
            Rectangle {
                width: 6 + (index % 2)
                height: width
                radius: width / 2
                color: colors.softAmber
                opacity: 0.84
                readonly property real angle: (root.orbitAngle + index * 92) * Math.PI / 180
                x: parent.width / 2 + Math.cos(angle) * (parent.width * (0.28 + (index % 2) * 0.12)) - width / 2
                y: parent.height / 2 + Math.sin(angle) * (parent.height * (0.22 + (index % 2) * 0.09)) - height / 2
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * (0.27 + root.pulseLevel * 0.08)
            height: width
            radius: width / 2
            color: Qt.rgba(0.95, 0.77, 0.62, 0.16)
            border.width: 1
            border.color: Qt.rgba(0.95, 0.77, 0.62, 0.32)
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.18
            height: width
            radius: width / 2
            color: colors.nebulaGold
        }

        Text {
            anchors.centerIn: parent
            text: root.symbol
            color: colors.neuralWhite
            font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.title
        }

        MouseArea {
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: root.activated()
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: core.y + core.height + 18
        spacing: 6

        Text {
            visible: root.label.length > 0
            text: root.label
            color: colors.neuralWhite
            font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.section
            horizontalAlignment: Text.AlignHCenter
            width: 260
        }

        Text {
            visible: root.subtitle.length > 0
            text: root.subtitle
            color: colors.dimText
            font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.small
            horizontalAlignment: Text.AlignHCenter
            width: 260
            wrapMode: Text.WordWrap
        }
    }
}
