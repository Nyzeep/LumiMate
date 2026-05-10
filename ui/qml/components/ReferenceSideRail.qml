import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string page: appBridge ? appBridge.currentPage : "home"
    property bool compact: height < 720

    width: 188

    Rectangle {
        anchors.fill: parent
        color: "#020713"
        opacity: 0.22
    }

    Rectangle {
        anchors.right: parent.right
        width: 1
        height: parent.height
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.12
    }

    Row {
        x: 30
        y: 28
        spacing: 12

        Text {
            text: "△"
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.72
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 31
        }

        Column {
            y: 0
            spacing: 3
            Text {
                text: appBridge.t("nav.brand", root.language)
                color: root.theme ? root.theme.text : "#F2EDE5"
                opacity: 0.92
                font.family: root.theme ? root.theme.display(root.language) : "SimSun"
                font.pixelSize: root.theme ? root.theme.typeBrand : 18
            }
            Text {
                text: appBridge.t("nav.subtitle", root.language)
                color: root.theme ? root.theme.muted : "#AEB8C3"
                opacity: 0.58
                font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
                font.pixelSize: 12
            }
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.compact ? 112 : 132
        spacing: root.compact ? 6 : 12
        ReferenceNavNode { compact: root.compact; theme: root.theme; motion: root.motion; language: root.language; label: appBridge.t("nav.home", root.language); glyph: "▲"; checked: root.page === "home"; onActivated: appBridge.navigate("home") }
        ReferenceNavNode { compact: root.compact; theme: root.theme; motion: root.motion; language: root.language; label: appBridge.t("nav.chat", root.language); glyph: "◌"; checked: root.page === "chat"; onActivated: appBridge.navigate("chat") }
        ReferenceNavNode { compact: root.compact; theme: root.theme; motion: root.motion; language: root.language; label: appBridge.t("nav.companion", root.language); glyph: "✧"; checked: root.page === "companion"; onActivated: appBridge.navigate("companion") }
        ReferenceNavNode { compact: root.compact; theme: root.theme; motion: root.motion; language: root.language; label: appBridge.t("nav.workbench", root.language); glyph: "⌂"; checked: root.page === "workbench"; onActivated: appBridge.navigate("workbench") }
        ReferenceNavNode { compact: root.compact; theme: root.theme; motion: root.motion; language: root.language; label: appBridge.t("nav.settings", root.language); glyph: "◎"; checked: root.page === "settings"; onActivated: appBridge.navigate("settings") }
    }

    Rectangle {
        id: profile
        x: 22
        width: parent.width - 44
        height: 88
        y: parent.height - height - 24
        visible: !root.compact
        radius: 42
        color: root.theme ? root.theme.panelSoft : "#15213A"
        opacity: 0.62
        border.width: 1
        border.color: Qt.rgba(0.79, 0.85, 0.89, 0.14)

        Rectangle {
            x: 14
            anchors.verticalCenter: parent.verticalCenter
            width: 52
            height: 52
            radius: 26
            color: root.theme ? root.theme.mistBlue : "#82A6BF"
            opacity: 0.26
            border.width: 1
            border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
            Rectangle {
                anchors.centerIn: parent
                width: 16
                height: 16
                radius: 8
                color: root.theme ? root.theme.moon : "#F3E1CE"
                opacity: 0.58
            }
        }

        Column {
            x: 76
            anchors.verticalCenter: parent.verticalCenter
            spacing: 4
            Text {
                text: appBridge.t("nav.profile.name", root.language)
                color: root.theme ? root.theme.text : "#F2EDE5"
                opacity: 0.84
                font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
                font.pixelSize: 14
            }
            Text {
                text: appBridge.t("nav.profile.subtitle", root.language)
                color: root.theme ? root.theme.muted : "#AEB8C3"
                opacity: 0.54
                font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
                font.pixelSize: 10
            }
            Rectangle {
                width: 54
                height: 2
                color: root.theme ? root.theme.accentSoft : "#F1A47A"
                opacity: 0.82
            }
        }
    }
}
