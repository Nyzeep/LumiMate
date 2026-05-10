import QtQuick
import QtQuick.Window

Item {
    id: root
    property var theme
    property var motion
    property var windowRef
    property string language: "zh-CN"

    width: 224
    height: 42

    Row {
        anchors.fill: parent
        spacing: 14

        Repeater {
            model: [
                { glyph: "♪", role: "music", tip: appBridge.t("shell.music", root.language) },
                { glyph: "−", role: "min", tip: appBridge.t("shell.minimize", root.language) },
                { glyph: "□", role: "max", tip: appBridge.t("shell.maximize", root.language) },
                { glyph: "×", role: "close", tip: appBridge.t("shell.close", root.language) }
            ]

            Item {
                width: 42
                height: 42
                property bool hovered: hit.containsMouse

                Rectangle {
                    anchors.fill: parent
                    radius: width / 2
                    color: "#09172B"
                    opacity: hovered ? 0.74 : 0.40
                    border.width: 1
                    border.color: hovered ? (root.theme ? root.theme.accentSoft : "#F1A47A") : Qt.rgba(0.79, 0.85, 0.89, 0.15)
                }

                Text {
                    anchors.centerIn: parent
                    text: modelData.glyph
                    color: root.theme ? root.theme.text : "#F2EDE5"
                    opacity: hovered ? 0.92 : 0.68
                    font.family: root.theme ? root.theme.sans(root.language) : "Segoe UI"
                    font.pixelSize: modelData.role === "music" ? 17 : 20
                }

                MouseArea {
                    id: hit
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: modelData.role === "music" ? Qt.ArrowCursor : Qt.PointingHandCursor
                    onClicked: {
                        if (!root.windowRef) {
                            return
                        }
                        if (modelData.role === "min") {
                            root.windowRef.showMinimized()
                        } else if (modelData.role === "max") {
                            root.windowRef.visibility = root.windowRef.visibility === Window.Maximized ? Window.Windowed : Window.Maximized
                        } else if (modelData.role === "close") {
                            Qt.quit()
                        }
                    }
                }
            }
        }
    }
}
