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
        color: Qt.rgba(0.02, 0.04, 0.08, 0.18)
    }

    Rectangle {
        anchors.right: parent.right
        width: 1
        height: parent.height
        color: colors.line
        opacity: 0.12
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 24
        spacing: 4

        Text {
            text: appBridge.t("nav.brand", appBridge.language)
            color: colors.neuralWhite
            font.family: typography.display(appBridge.language)
            font.pixelSize: 22
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
        }
        Text {
            text: appBridge.t(appBridge.currentSceneGroupLabelKey, appBridge.language)
            color: colors.dimText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.micro
            horizontalAlignment: Text.AlignHCenter
            width: 84
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: 148
        spacing: 20

        Repeater {
            model: appBridge.currentSceneGroupScenes

            Item {
                width: 92
                height: 70

                HaloIconButton {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 0
                    diameter: 42
                    symbol: modelData.icon
                    active: root.page === modelData.id
                    onActivated: appBridge.navigate(modelData.id)
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 50
                    width: 88
                    text: appBridge.t(modelData.labelKey, appBridge.language)
                    color: root.page === modelData.id ? colors.neuralWhite : colors.dimText
                    opacity: root.page === modelData.id ? 0.92 : 0.56
                    horizontalAlignment: Text.AlignHCenter
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.micro
                }
            }
        }
    }

    Column {
        anchors.horizontalCenter: parent.horizontalCenter
        y: parent.height - 78
        spacing: 6

        Repeater {
            model: 3
            Rectangle {
                anchors.horizontalCenter: parent ? parent.horizontalCenter : undefined
                width: index === 0 ? 18 : 6
                height: 2
                radius: 1
                color: index === 0 ? colors.softAmber : colors.line
                opacity: 0.78 - index * 0.18
            }
        }
    }
}
