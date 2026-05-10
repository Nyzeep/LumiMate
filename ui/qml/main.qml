import QtQuick
import QtQuick.Window
import "scenes"

Window {
    id: window
    width: 1280
    height: 760
    minimumWidth: 1040
    minimumHeight: 680
    visible: true
    color: "transparent"
    title: "LumiMate"
    flags: Qt.Window | Qt.FramelessWindowHint

    SceneHost {
        anchors.fill: parent
        windowRef: window
    }
}
