import QtQuick
import "../components"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property bool active: false

    visible: opacity > 0.01
    opacity: active ? 1 : 0
    scale: active ? 1 : 0.97

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

    Text {
        x: 30
        y: 22
        text: appBridge.t("companion.title", root.language)
        color: root.theme ? root.theme.textWarm : "#F4D4C3"
        opacity: 0.92
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeTitle : 32
        font.weight: Font.DemiBold
    }

    Text {
        x: 32
        y: 70
        width: Math.min(parent.width * 0.62, 620)
        text: appBridge.t("companion.subtitle", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.66
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        wrapMode: Text.WordWrap
    }

    CompanionStage {
        x: parent.width * 0.12
        y: 110
        width: parent.width * 0.76
        height: parent.height - 144
        theme: root.theme
        motion: root.motion
        language: root.language
    }
}
