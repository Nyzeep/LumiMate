import QtQuick

Rectangle {
    id: root
    property color glowColor: "#F2C29D"
    property real glowOpacity: 0.16
    width: 320
    height: 320
    radius: width / 2
    color: glowColor
    opacity: glowOpacity
}
