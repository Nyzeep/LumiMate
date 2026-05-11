import QtQuick
import QtQuick.Effects
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    property string mood: emotionBridge ? emotionBridge.mood : "quiet"
    property string sceneId: appBridge ? appBridge.currentPage : "home"
    readonly property string backgroundUrl: appBridge ? appBridge.sceneBackgroundUrl(root.sceneId) : ""

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: colors.inkAbyss }
            GradientStop { position: 0.45; color: colors.inkDeep }
            GradientStop { position: 1.0; color: colors.inkSpace }
        }
    }

    Image {
        id: backgroundSource
        anchors.fill: parent
        source: root.backgroundUrl
        fillMode: Image.PreserveAspectCrop
        visible: true
        smooth: true
    }

    ShaderEffectSource {
        id: backgroundCapture
        anchors.fill: parent
        sourceItem: backgroundSource
        hideSource: true
        live: true
    }

    MultiEffect {
        anchors.fill: parent
        source: backgroundCapture
        blurEnabled: true
        blur: 0.72
        blurMax: 72
        brightness: 0.16
        saturation: -0.15
        opacity: 0.34
        autoPaddingEnabled: true
    }

    Image {
        anchors.fill: parent
        source: root.backgroundUrl
        fillMode: Image.PreserveAspectCrop
        smooth: true
        opacity: root.sceneId === "companion" ? 0.90 : root.sceneId === "storage" ? 0.56 : 0.68
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0.01, 0.02, 0.05, 0.42)
    }

    AmbientGlow {
        x: root.width * 0.62
        y: root.height * 0.12
        width: root.width * 0.36
        height: width
        glowColor: colors.nebulaGold
        glowOpacity: root.mood === "awakening" ? 0.26 : root.mood === "replying" ? 0.20 : root.sceneId === "companion" ? 0.22 : 0.12
    }

    AmbientGlow {
        x: -width * 0.08
        y: root.height * 0.46
        width: root.width * 0.24
        height: width
        glowColor: colors.silentViolet
        glowOpacity: 0.08
    }

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: Qt.rgba(0.00, 0.00, 0.00, 0.24) }
            GradientStop { position: 0.52; color: "transparent" }
            GradientStop { position: 1.0; color: Qt.rgba(0.01, 0.01, 0.04, 0.38) }
        }
    }

    ParticleField {
        anchors.fill: parent
        particleCount: root.sceneId === "companion" ? 68 : 58
        intensity: root.mood === "listening" ? 0.72 : root.mood === "thinking" ? 0.58 : 0.40
    }

    Repeater {
        model: [0.18, 0.54, 0.91]
        Rectangle {
            x: root.width * modelData
            y: 0
            width: 1
            height: root.height
            color: colors.line
            opacity: 0.05
        }
    }

    Repeater {
        model: [0.28, 0.46, 0.72]
        Rectangle {
            x: root.width * modelData
            y: root.height * 0.82
            width: root.width * (0.22 + index * 0.12)
            height: 1
            radius: 1
            color: Qt.rgba(0.95, 0.77, 0.62, 0.10 - index * 0.02)
        }
    }
}
