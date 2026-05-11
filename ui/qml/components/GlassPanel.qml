import QtQuick
import QtQuick.Effects
import "../design_system"

Item {
    id: root
    Colors { id: colors }

    property string tone: "soft"
    property real radius: 28
    property real padding: 20
    property color fillColor: tone === "strong" ? Qt.rgba(0.05, 0.10, 0.19, 0.82) : Qt.rgba(0.05, 0.10, 0.18, 0.52)
    property color edgeColor: tone === "strong" ? Qt.rgba(0.94, 0.78, 0.63, 0.22) : Qt.rgba(0.65, 0.59, 0.72, 0.18)
    property color glowColor: colors.nebulaGold
    property real glowOpacity: tone === "strong" ? 0.12 : 0.06
    default property alias contentData: content.data

    Item {
        id: glowSource
        anchors.fill: parent

        Rectangle {
            anchors.fill: parent
            radius: root.radius
            color: root.glowColor
            opacity: 0.92
        }
    }

    ShaderEffectSource {
        id: glowCapture
        anchors.fill: parent
        sourceItem: glowSource
        hideSource: true
        live: true
    }

    MultiEffect {
        anchors.fill: parent
        source: glowCapture
        blurEnabled: true
        blur: 1.0
        blurMax: 72
        brightness: 0.18
        saturation: -0.15
        opacity: root.glowOpacity
        autoPaddingEnabled: true
    }

    Rectangle {
        anchors.fill: parent
        radius: root.radius
        color: root.fillColor
        border.width: 1
        border.color: root.edgeColor
    }

    Rectangle {
        anchors.fill: parent
        radius: root.radius
        color: "transparent"
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.03)
        anchors.margins: 1
    }

    Item {
        id: content
        anchors.fill: parent
        anchors.margins: root.padding
    }
}
