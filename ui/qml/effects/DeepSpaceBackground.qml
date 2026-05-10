import QtQuick
import "../geometry"
import "../particles"

Item {
    id: root
    property var theme
    property var motion

    ShaderHost {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
    }

    Image {
        anchors.fill: parent
        source: appBridge ? appBridge.assetUrl("atmosphereTexture") : ""
        fillMode: Image.PreserveAspectCrop
        opacity: status === Image.Ready ? 0.10 : 0
        asynchronous: true
    }

    OrbitalField {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
        density: 1.18
        opacity: 0.86
    }

    ParticleMist {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
        density: root.theme ? root.theme.particleDensity : 0.58
    }

    Rectangle {
        anchors.fill: parent
        color: "#000000"
        opacity: 0.18
    }
}
