import QtQuick
import "../components"

Item {
    id: root
    property var windowRef

    SpaceBackground {
        anchors.fill: parent
    }

    RitualRail {
        id: rail
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
    }

    Item {
        anchors.left: rail.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom

        WindowControls {
            id: controls
            anchors.top: parent.top
            anchors.right: parent.right
            anchors.margins: 22
            windowRef: root.windowRef
        }

        MouseArea {
            anchors.left: parent.left
            anchors.right: controls.left
            anchors.top: parent.top
            height: 44
            acceptedButtons: Qt.LeftButton
            onPressed: {
                if (root.windowRef && root.windowRef.startSystemMove) {
                    root.windowRef.startSystemMove()
                }
            }
        }

        Loader {
            id: pageLoader
            anchors.fill: parent
            anchors.margins: 26
            sourceComponent: appBridge.currentPage === "home" ? homeScene
                : appBridge.currentPage === "chat" ? chatScene
                : appBridge.currentPage === "companion" ? companionScene
                : appBridge.currentPage === "workbench" ? workbenchScene
                : settingsScene
        }
    }

    Component { id: homeScene; HomeScene {} }
    Component { id: chatScene; ChatScene {} }
    Component { id: companionScene; CompanionScene {} }
    Component { id: workbenchScene; WorkbenchScene {} }
    Component { id: settingsScene; SettingsScene {} }
}
