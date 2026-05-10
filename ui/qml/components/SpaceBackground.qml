import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    property string mood: emotionBridge ? emotionBridge.mood : "quiet"

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: colors.inkAbyss }
            GradientStop { position: 0.45; color: colors.inkDeep }
            GradientStop { position: 1.0; color: colors.inkSpace }
        }
    }

    AmbientGlow {
        x: root.width * 0.58
        y: root.height * 0.16
        width: root.width * 0.34
        height: width
        glowColor: colors.nebulaGold
        glowOpacity: root.mood === "awakening" ? 0.18 : root.mood === "replying" ? 0.14 : 0.10
    }

    AmbientGlow {
        x: -width * 0.18
        y: root.height * 0.5
        width: root.width * 0.28
        height: width
        glowColor: colors.silentViolet
        glowOpacity: 0.08
    }

    ParticleField {
        anchors.fill: parent
        particleCount: 56
        intensity: root.mood === "listening" ? 0.72 : root.mood === "thinking" ? 0.58 : 0.40
    }

    Repeater {
        model: [0.26, 0.54, 0.81]
        Rectangle {
            x: root.width * modelData
            y: 0
            width: 1
            height: root.height
            color: colors.line
            opacity: 0.06
        }
    }
}
