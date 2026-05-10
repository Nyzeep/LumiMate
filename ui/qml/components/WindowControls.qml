import QtQuick
import QtQuick.Window
import "../design_system"

Row {
    id: root
    Colors { id: colors }
    property var windowRef
    spacing: 12

    Repeater {
        model: [
            { label: "-", action: "min" },
            { label: "[]", action: "max" },
            { label: "x", action: "close" }
        ]

        Rectangle {
            width: 28
            height: 28
            radius: 14
            color: Qt.rgba(0.08, 0.12, 0.20, 0.54)
            border.width: 1
            border.color: Qt.rgba(0.60, 0.69, 0.82, 0.20)

            Text {
                anchors.centerIn: parent
                text: modelData.label
                color: colors.quietText
                font.pixelSize: 13
            }

            MouseArea {
                anchors.fill: parent
                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (!root.windowRef) {
                        return
                    }
                    if (modelData.action === "min") {
                        root.windowRef.showMinimized()
                    } else if (modelData.action === "max") {
                        if (root.windowRef.visibility === Window.Maximized) {
                            root.windowRef.showNormal()
                        } else {
                            root.windowRef.showMaximized()
                        }
                    } else if (modelData.action === "close") {
                        root.windowRef.close()
                    }
                }
            }
        }
    }
}
