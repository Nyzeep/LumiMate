import QtQuick
import "../geometry"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"

    OrbitalField {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
        density: 0.95
        opacity: 0.58
    }

    Rectangle {
        id: moon
        width: Math.min(parent.width, parent.height) * 0.48
        height: width
        radius: width / 2
        x: parent.width * 0.42
        y: parent.height * 0.23
        color: root.theme ? root.theme.moonPale : "#F7D9CA"
        opacity: 0.72
        SequentialAnimation on scale {
            loops: Animation.Infinite
            NumberAnimation { to: 1.035; duration: 7000; easing.type: Easing.InOutSine }
            NumberAnimation { to: 0.985; duration: 7000; easing.type: Easing.InOutSine }
        }
    }

    Rectangle {
        x: moon.x + moon.width * 0.53
        y: moon.y
        width: moon.width * 0.50
        height: moon.height
        color: root.theme ? root.theme.inkDeep : "#020713"
        opacity: 0.62
    }

    Repeater {
        model: 4
        Rectangle {
            width: moon.width * (0.13 + index * 0.035)
            height: moon.height * (0.76 - index * 0.08)
            radius: width / 2
            x: moon.x + moon.width * (0.48 + index * 0.16)
            y: moon.y + moon.height * (0.22 + index * 0.06)
            color: root.theme ? root.theme.ink : "#071120"
            opacity: 0.74 - index * 0.08
            border.width: 1
            border.color: Qt.rgba(0.79, 0.85, 0.89, 0.13)
        }
    }

    Repeater {
        model: 8
        Rectangle {
            width: moon.width * 0.42 + index * 22
            height: 24
            x: moon.x - 82 + index * 30
            y: moon.y + moon.height * 0.86 + index * 14
            color: root.theme ? root.theme.ink : "#071120"
            opacity: 0.76 - index * 0.035
            border.width: 1
            border.color: Qt.rgba(0.79, 0.85, 0.89, 0.08)
        }
    }

    Item {
        id: presenceAnchor
        width: 52
        height: 92
        x: moon.x + moon.width * 0.16
        y: moon.y + moon.height * 0.62
        opacity: 0.30

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 2
            width: 17
            height: 17
            radius: 9
            color: root.theme ? root.theme.moon : "#F3E1CE"
        }
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 24
            width: 20
            height: 54
            radius: 9
            color: root.theme ? root.theme.textWarm : "#F4D4C3"
        }
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            y: 75
            width: 40
            height: 2
            color: root.theme ? root.theme.line : "#C9D9E2"
            opacity: 0.42
        }
    }

    Repeater {
        model: 9
        Rectangle {
            width: 3 + index % 4
            height: width
            radius: width / 2
            x: parent.width * (0.10 + ((index * 17) % 78) / 100)
            y: parent.height * (0.12 + ((index * 29) % 70) / 100)
            color: index % 3 === 0 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
            opacity: 0.32
        }
    }

    Item {
        id: flowers
        x: moon.x - 150
        y: moon.y + moon.height * 0.72
        width: 150
        height: 150
        opacity: 0.44

        Repeater {
            model: 5
            Rectangle {
                width: 1
                height: 80 - index * 8
                x: 48 + index * 16
                y: 42 + index * 6
                rotation: -28 + index * 12
                color: root.theme ? root.theme.line : "#C9D9E2"
                opacity: 0.20
            }
        }
        Repeater {
            model: 12
            Rectangle {
                width: 8
                height: 8
                radius: 4
                x: 30 + ((index * 19) % 92)
                y: 16 + ((index * 31) % 86)
                color: root.theme ? root.theme.accentSoft : "#F1A47A"
                opacity: 0.38
            }
        }
    }
}
