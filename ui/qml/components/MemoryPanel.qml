import QtQuick

Item {
    id: root
    property var theme
    property string language: "zh-CN"

    width: 456
    height: 214

    Rectangle {
        anchors.fill: parent
        radius: root.theme ? root.theme.radiusCard : 22
        color: root.theme ? root.theme.panelSoft : "#15213A"
        opacity: 0.46
        border.width: 1
        border.color: Qt.rgba(0.79, 0.85, 0.89, 0.16)
    }

    Rectangle {
        x: 26
        y: 30
        width: 6
        height: 6
        radius: 3
        color: root.theme ? root.theme.accentSoft : "#F1A47A"
    }

    Text {
        x: 42
        y: 24
        text: appBridge.t("home.notes.title", root.language)
        color: root.theme ? root.theme.textWarm : "#F4D4C3"
        opacity: 0.90
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeCardTitle : 18
    }

    Text {
        anchors.right: parent.right
        anchors.rightMargin: 32
        y: 22
        text: "✎"
        color: root.theme ? root.theme.moon : "#F3E1CE"
        opacity: 0.70
        font.pixelSize: 22
    }

    Rectangle {
        x: 28
        y: 62
        width: parent.width - 56
        height: 1
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.08
    }

    Text {
        x: 42
        y: 96
        width: parent.width * 0.62
        text: appBridge.t("home.notes.body1", root.language) + "\n" + appBridge.t("home.notes.body2", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.66
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        lineHeight: 1.45
        wrapMode: Text.WordWrap
    }

    Item {
        anchors.right: parent.right
        anchors.rightMargin: 28
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        width: 132
        height: 24

        Text {
            anchors.right: arrow.left
            anchors.rightMargin: 10
            anchors.verticalCenter: parent.verticalCenter
            text: appBridge.t("home.notes.more", root.language)
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.66
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: 12
        }
        Text {
            id: arrow
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: "→"
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.68
            font.pixelSize: 18
        }
    }
}
