import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string state: modelBridge ? modelBridge.state : "idle"
    property string message: modelBridge && modelBridge.stateMessage !== "Waiting" ? modelBridge.stateMessage : appBridge.t("workbench.progressQuiet", root.language)
    property real progress: modelBridge && modelBridge.progressTotal > 0 ? modelBridge.progressStep / modelBridge.progressTotal : (modelBridge && modelBridge.loaded ? 1 : 0)

    height: 210

    Item {
        id: core
        width: 150
        height: 150
        anchors.left: parent.left
        anchors.leftMargin: 18
        anchors.verticalCenter: parent.verticalCenter

        Rectangle {
            anchors.centerIn: parent
            width: 150
            height: 150
            radius: 75
            color: root.theme ? root.theme.accent : "#D97855"
            opacity: 0.045 + progress * 0.06
        }

        Repeater {
            model: 4
            Rectangle {
                anchors.centerIn: parent
                width: 74 + index * 30
                height: width
                radius: width / 2
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.line : "#C9D9E2")
                opacity: 0.14 + progress * 0.18 - index * 0.02
                RotationAnimation on rotation {
                    from: 0
                    to: 360
                    duration: (root.motion ? root.motion.deepOrbitDuration : 52000) + index * 7000
                    loops: Animation.Infinite
                    running: true
                }
            }
        }

        Rectangle {
            anchors.centerIn: parent
            width: 20 + progress * 8
            height: width
            radius: width / 2
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.68 + progress * 0.24
        }
    }

    Text {
        text: state === "idle" ? appBridge.t("workbench.progressQuiet", root.language) : state
        x: core.x + core.width + 48
        y: 55
        width: parent.width - x - 24
        color: root.theme ? root.theme.text : "#F2EDE5"
        opacity: 0.90
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeCardValue : 28
        font.weight: Font.DemiBold
        elide: Text.ElideRight
    }

    Text {
        text: message
        x: core.x + core.width + 50
        y: 98
        width: parent.width - x - 24
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.72
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        wrapMode: Text.WordWrap
    }

    Rectangle {
        x: core.x + core.width + 50
        y: 154
        width: Math.max(120, parent.width - x - 70)
        height: 2
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.13
        Rectangle {
            width: parent.width * Math.max(0, Math.min(1, root.progress))
            height: parent.height
            color: root.theme ? root.theme.accentSoft : "#F1A47A"
            opacity: 0.72
        }
    }
}
