import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    Motion { id: motion }
    property real progress: modelBridge && modelBridge.progressTotal > 0 ? modelBridge.progressStep / modelBridge.progressTotal : (modelBridge && modelBridge.loaded ? 1 : 0)
    property string stage: modelBridge ? modelBridge.state : "idle"
    property string centerLabel: Math.round(root.progress * 100) + "%"
    property string footerLabel: modelBridge ? modelBridge.stateMessage : ""
    property real orbitAngle: 0

    NumberAnimation on orbitAngle {
        from: 0
        to: 360
        duration: motion.orbitDuration
        loops: Animation.Infinite
        running: root.visible && !appBridge.reduceMotion
    }

    Item {
        anchors.centerIn: parent
        width: Math.min(root.width, root.height) * 0.8
        height: width

        AmbientGlow {
            anchors.centerIn: parent
            width: parent.width * 1.3
            height: width
            glowColor: colors.nebulaGold
            glowOpacity: 0.20
        }

        Repeater {
            model: 5
            Rectangle {
                anchors.centerIn: parent
                width: parent.width * (0.22 + index * 0.13)
                height: width
                radius: width / 2
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0 ? colors.nebulaGold : colors.line
                opacity: 0.18 + root.progress * 0.22 - index * 0.02
            }
        }

        Repeater {
            model: 6
            Rectangle {
                width: 6
                height: 6
                radius: 3
                color: colors.softAmber
                readonly property real angle: (root.orbitAngle + index * 60) * Math.PI / 180
                x: parent.width / 2 + Math.cos(angle) * (parent.width * 0.32) - width / 2
                y: parent.height / 2 + Math.sin(angle) * (parent.height * 0.28) - height / 2
                opacity: 0.68
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * (0.08 + root.progress * 0.06)
            height: width
            radius: width / 2
            color: colors.nebulaGold
            opacity: 0.86
        }

        Text {
            anchors.centerIn: parent
            text: root.centerLabel
            color: colors.neuralWhite
            font.family: typography.display("en-US")
            font.pixelSize: 26
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            y: parent.height - 8
            text: root.footerLabel
            color: colors.dimText
            font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: 12
        }
    }
}
