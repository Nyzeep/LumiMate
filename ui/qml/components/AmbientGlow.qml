import QtQuick
import QtQuick.Effects

Item {
    id: root
    property color glowColor: "#F2C29D"
    property real glowOpacity: 0.18
    property real coreScale: 0.36

    Item {
        id: glowSource
        anchors.fill: parent

        Rectangle {
            anchors.centerIn: parent
            width: parent.width * root.coreScale
            height: parent.height * root.coreScale
            radius: width / 2
            color: root.glowColor
            opacity: 0.96
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
        blurMax: 96
        brightness: 0.25
        saturation: -0.15
        opacity: root.glowOpacity
        autoPaddingEnabled: true
    }
}
