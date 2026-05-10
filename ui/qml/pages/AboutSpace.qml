import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property bool active: false

    visible: opacity > 0.01
    opacity: active ? 1 : 0
    scale: active ? 1 : 0.97

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

    function updateSourceText() {
        if (!appBridge || appBridge.updateSource.length === 0 || appBridge.updateSource === "Not configured") {
            return appBridge.t("about.not_configured", root.language)
        }
        return appBridge.updateSource
    }

    Text {
        x: 30
        y: 28
        text: appBridge.t("about.title", root.language)
        color: root.theme ? root.theme.textWarm : "#F4D4C3"
        opacity: 0.92
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeTitle : 32
        font.weight: Font.DemiBold
    }

    Text {
        x: 32
        y: 78
        width: Math.min(parent.width * 0.66, 640)
        text: appBridge.t("about.subtitle", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.68
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        wrapMode: Text.WordWrap
    }

    Item {
        id: orbitMark
        x: parent.width - width - 92
        y: 92
        width: 230
        height: 230
        opacity: 0.62

        Repeater {
            model: 4
            Rectangle {
                anchors.centerIn: parent
                width: 72 + index * 46
                height: width
                radius: width / 2
                color: "transparent"
                border.width: 1
                border.color: root.theme ? root.theme.line : "#C9D9E2"
                opacity: 0.18 - index * 0.025
            }
        }
        Rectangle {
            anchors.centerIn: parent
            width: 22
            height: 22
            radius: 11
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.68
        }
        RotationAnimation on rotation {
            from: 0
            to: 360
            duration: root.motion ? root.motion.deepOrbitDuration : 52000
            loops: Animation.Infinite
            running: true
        }
    }

    Column {
        id: facts
        x: 34
        y: 154
        width: Math.min(parent.width * 0.70, 760)
        spacing: 18

        Repeater {
            model: [
                { key: "about.version", value: appBridge ? appBridge.appVersion : "0.1.0" },
                { key: "about.author", value: appBridge ? appBridge.appAuthor : "LumiMate Team" },
                { key: "about.runtime", value: "Python + PyQt6 + QtQuick/QML" },
                { key: "about.python", value: appBridge ? appBridge.pythonExecutable : "" },
                { key: "about.project", value: appBridge ? appBridge.projectRoot : "" },
                { key: "about.update", value: root.updateSourceText() }
            ]

            Item {
                width: facts.width
                height: modelData.key === "about.python" || modelData.key === "about.project" ? 44 : 34

                Rectangle {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    width: 6
                    height: 6
                    radius: 3
                    color: root.theme ? root.theme.accentSoft : "#F1A47A"
                    opacity: 0.70
                }

                Text {
                    x: 22
                    anchors.verticalCenter: parent.verticalCenter
                    width: 130
                    text: appBridge.t(modelData.key, root.language)
                    color: root.theme ? root.theme.muted : "#AEB8C3"
                    opacity: 0.58
                    font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
                    font.pixelSize: root.theme ? root.theme.typeSmall : 12
                }

                Text {
                    x: 168
                    anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - x
                    text: modelData.value
                    color: root.theme ? root.theme.text : "#F2EDE5"
                    opacity: 0.82
                    font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
                    font.pixelSize: root.theme ? root.theme.typeBody : 14
                    elide: Text.ElideMiddle
                }
            }
        }
    }

    Text {
        x: 34
        y: parent.height - 84
        width: Math.min(parent.width * 0.62, 640)
        text: appBridge.t("about.note", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.58
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeSmall : 12
        wrapMode: Text.WordWrap
    }
}
