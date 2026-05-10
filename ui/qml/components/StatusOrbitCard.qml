import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"

    width: 456
    height: 320

    Rectangle {
        anchors.fill: parent
        radius: root.theme ? root.theme.radiusCard : 22
        color: root.theme ? root.theme.panelSoft : "#15213A"
        opacity: 0.54
        border.width: 1
        border.color: Qt.rgba(0.79, 0.85, 0.89, 0.17)
    }

    Rectangle {
        x: 26
        y: 28
        width: 6
        height: 6
        radius: 3
        color: root.theme ? root.theme.accentSoft : "#F1A47A"
    }

    Text {
        x: 42
        y: 22
        text: appBridge.t("home.status.title", root.language)
        color: root.theme ? root.theme.textWarm : "#F4D4C3"
        opacity: 0.90
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeCardTitle : 18
    }

    Text {
        anchors.right: parent.right
        anchors.rightMargin: 32
        y: 24
        text: "•  " + appBridge.t("home.status.online", root.language)
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.70
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: 13
    }

    Rectangle {
        x: 28
        y: 62
        width: parent.width - 56
        height: 1
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.08
    }

    Item {
        id: radar
        x: 42
        y: 82
        width: 190
        height: 190

        Repeater {
            model: 4
            Rectangle {
                anchors.centerIn: parent
                width: 62 + index * 38
                height: width
                radius: width / 2
                color: "transparent"
                border.width: 1
                border.color: Qt.rgba(0.79, 0.85, 0.89, 0.13 - index * 0.015)
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: 40
            height: 40
            radius: 20
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.12 + (emotionBridge ? emotionBridge.presenceLevel * 0.10 : 0.06)
        }

        Rectangle {
            anchors.centerIn: parent
            width: 11
            height: 11
            radius: 6
            color: root.theme ? root.theme.moonPale : "#F7D9CA"
            opacity: 0.92
        }

        Rectangle {
            width: 13
            height: 13
            radius: 7
            color: root.theme ? root.theme.accentSoft : "#F1A47A"
            opacity: 0.74
            x: parent.width / 2 + Math.cos(radar.rotation / 57.3) * 72 - width / 2
            y: parent.height / 2 + Math.sin(radar.rotation / 57.3) * 54 - height / 2
        }

        RotationAnimation on rotation {
            from: 0
            to: 360
            duration: 42000
            loops: Animation.Infinite
            running: true
        }
    }

    Column {
        x: 252
        y: 96
        width: parent.width - x - 36
        spacing: 12

        Text {
            text: appBridge.t("home.status.mood", root.language)
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.60
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: 13
        }
        Text {
            text: appBridge.t("home.status.moodValue", root.language)
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.95
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: root.theme ? root.theme.typeCardValue : 30
        }
        Text {
            text: appBridge.t("home.status.memory", root.language)
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.58
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: 13
        }
        Text {
            text: "86%"
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.86
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 25
        }
        Rectangle {
            width: 154
            height: 3
            color: Qt.rgba(0.79, 0.85, 0.89, 0.08)
            Rectangle {
                width: parent.width * 0.86
                height: parent.height
                color: root.theme ? root.theme.accentSoft : "#F1A47A"
                opacity: 0.88
            }
        }
        Text {
            text: appBridge.t("home.status.voice", root.language)
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.58
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: 13
        }
        Text {
            text: chatBridge && chatBridge.running ? appBridge.t("chat.status.listening", root.language) : appBridge.t("home.status.standby", root.language)
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.78
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 18
        }
    }
}
