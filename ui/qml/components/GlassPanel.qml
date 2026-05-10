import QtQuick

Rectangle {
    id: root
    property string tone: "soft"
    color: tone === "strong" ? Qt.rgba(0.05, 0.10, 0.19, 0.76) : Qt.rgba(0.06, 0.10, 0.18, 0.52)
    radius: 26
    border.width: 1
    border.color: tone === "strong" ? Qt.rgba(0.89, 0.74, 0.62, 0.24) : Qt.rgba(0.60, 0.69, 0.82, 0.18)
}
