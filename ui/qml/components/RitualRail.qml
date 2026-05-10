import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    Geometry { id: geometry }
    property string page: appBridge ? appBridge.currentPage : "home"
    width: geometry.railWidth

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0.02, 0.04, 0.08, 0.24)
    }

    Rectangle {
        anchors.right: parent.right
        width: 1
        height: parent.height
        color: colors.line
        opacity: 0.14
    }

    Column {
        x: 24
        y: 28
        spacing: 4

        Text {
            text: appBridge.t("nav.brand", appBridge.language)
            color: colors.neuralWhite
            font.family: typography.display(appBridge.language)
            font.pixelSize: 24
        }
        Text {
            text: appBridge.t("nav.subtitle", appBridge.language)
            color: colors.dimText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.small
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 132
        spacing: 14

        Repeater {
            model: [
                { id: "home", label: appBridge.t("nav.home", appBridge.language) },
                { id: "chat", label: appBridge.t("nav.chat", appBridge.language) },
                { id: "companion", label: appBridge.t("nav.companion", appBridge.language) },
                { id: "workbench", label: appBridge.t("nav.workbench", appBridge.language) },
                { id: "settings", label: appBridge.t("nav.settings", appBridge.language) }
            ]

            Item {
                width: 96
                height: 58

                Rectangle {
                    anchors.centerIn: parent
                    width: 48
                    height: 48
                    radius: 24
                    color: root.page === modelData.id ? Qt.rgba(0.95, 0.77, 0.62, 0.10) : Qt.rgba(0.10, 0.15, 0.24, 0.34)
                    border.width: 1
                    border.color: root.page === modelData.id ? Qt.rgba(0.95, 0.77, 0.62, 0.44) : Qt.rgba(0.60, 0.69, 0.82, 0.18)
                }

                Rectangle {
                    anchors.centerIn: parent
                    width: root.page === modelData.id ? 12 : 8
                    height: width
                    radius: width / 2
                    color: root.page === modelData.id ? colors.nebulaGold : colors.line
                    opacity: root.page === modelData.id ? 0.96 : 0.56
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: appBridge.navigate(modelData.id)
                }
            }
        }
    }

    Column {
        x: 24
        y: parent.height - 88
        spacing: 2

        Text {
            text: appBridge.t("nav.profile.name", appBridge.language)
            color: colors.quietText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.body
        }
        Text {
            text: appBridge.t("nav.profile.subtitle", appBridge.language)
            color: colors.dimText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.micro
        }
    }
}
