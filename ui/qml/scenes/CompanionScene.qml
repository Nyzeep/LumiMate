import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    Text {
        x: 28
        y: 76
        text: appBridge.t("companion.title", appBridge.language)
        color: colors.neuralWhite
        font.family: typography.display(appBridge.language)
        font.pixelSize: typography.title
    }

    Text {
        x: 28
        y: 116
        width: root.width * 0.34
        text: appBridge.t("companion.subtitle", appBridge.language)
        wrapMode: Text.WordWrap
        color: colors.dimText
        font.family: typography.sans(appBridge.language)
        font.pixelSize: typography.body
    }

    GlassPanel {
        x: 28
        y: 188
        width: 300
        height: 180

        Column {
            x: 18
            y: 18
            spacing: 10
            Text {
                text: appBridge.t("companion.stage.adapter", appBridge.language)
                color: colors.dimText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
            Text {
                text: companionBridge.rendererType
                color: colors.neuralWhite
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.title
            }
            Text {
                width: parent.width - 12
                text: companionBridge.rendererCapability
                wrapMode: Text.WordWrap
                color: colors.quietText
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }
            Text {
                text: companionBridge.rendererReady ? appBridge.t("companion.stage.ready", appBridge.language) : appBridge.t("companion.stage.pending", appBridge.language)
                color: companionBridge.rendererReady ? colors.success : colors.softAmber
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.small
            }
        }
    }

    Item {
        x: root.width * 0.32
        y: 96
        width: root.width * 0.60
        height: root.height - 150

        EmotionPulse {
            anchors.centerIn: parent
            width: parent.width * 0.76
            height: width
        }

        Image {
            anchors.centerIn: parent
            width: parent.width * 0.72
            height: parent.height * 0.84
            source: appBridge.assetUrl("companionPortrait")
            fillMode: Image.PreserveAspectFit
            opacity: 0.74
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            width: parent.width * 0.58
            height: 18
            radius: 9
            color: Qt.rgba(0.95, 0.77, 0.62, 0.08)
        }
    }
}
