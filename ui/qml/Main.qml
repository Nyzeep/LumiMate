import QtQuick
import QtQuick.Window
import "layouts"

Window {
    id: window
    width: 1280
    height: 760
    minimumWidth: 920
    minimumHeight: 600
    visible: true
    color: "transparent"
    title: "LumiMate"
    flags: Qt.Window | Qt.FramelessWindowHint

    RootScene {
        anchors.fill: parent
        windowRef: window
    }
}
