import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    property var windowRef
    Colors { id: colors }
    Typography { id: typography }

    SpaceBackground {
        anchors.fill: parent
        sceneId: appBridge.currentPage
    }

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.width: 1
        border.color: Qt.rgba(0.95, 0.77, 0.62, 0.12)
    }

    RitualRail {
        id: rail
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
    }

    Item {
        id: stage
        anchors.left: rail.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        Rectangle {
            anchors.fill: parent
            anchors.margins: 16
            radius: 30
            color: Qt.rgba(0.03, 0.05, 0.10, 0.08)
            border.width: 1
            border.color: Qt.rgba(0.95, 0.77, 0.62, 0.14)
        }

        Rectangle {
            anchors.fill: parent
            anchors.leftMargin: 30
            anchors.rightMargin: 30
            anchors.topMargin: 28
            anchors.bottomMargin: 28
            color: "transparent"
            border.width: 1
            border.color: Qt.rgba(0.62, 0.69, 0.82, 0.10)
        }

        Column {
            x: 48
            y: 28
            spacing: 4

            Text {
                text: appBridge.t(appBridge.currentSceneGroupLabelKey, appBridge.language)
                color: colors.softAmber
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.section
            }

            Text {
                text: appBridge.t(appBridge.currentSceneGroupSubtitleKey, appBridge.language)
                color: colors.dimText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
        }

        WindowControls {
            id: controls
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.topMargin: 24
            anchors.rightMargin: 32
            windowRef: root.windowRef
        }

        MouseArea {
            anchors.left: parent.left
            anchors.right: controls.left
            anchors.top: parent.top
            height: 54
            acceptedButtons: Qt.LeftButton
            onPressed: {
                if (root.windowRef && root.windowRef.startSystemMove) {
                    root.windowRef.startSystemMove()
                }
            }
        }

        Loader {
            id: pageLoader
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.leftMargin: 48
            anchors.rightMargin: 44
            anchors.topMargin: 98
            anchors.bottomMargin: 38
            source: appBridge.sceneComponent(appBridge.currentPage)
        }

        Item {
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.leftMargin: 40
            anchors.bottomMargin: 22
            width: 86
            height: 12

            Repeater {
                model: 3

                Rectangle {
                    x: index === 0 ? 0 : 22 + (index - 1) * 10
                    y: 5
                    width: index === 0 ? 18 : 6
                    height: 2
                    radius: 1
                    color: index === 0 ? colors.softAmber : colors.line
                    opacity: 0.84 - index * 0.16
                }
            }
        }
    }
}
