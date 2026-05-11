import QtQuick
import QtQuick.Window
import "scenes"

Window {
    id: window
    width: 1600
    height: 900
    minimumWidth: 1280
    minimumHeight: 720
    visible: true
    color: "transparent"
    title: "LumiMate"
    flags: Qt.Window | Qt.FramelessWindowHint

    SceneHost {
        anchors.fill: parent
        windowRef: window
    }
}
