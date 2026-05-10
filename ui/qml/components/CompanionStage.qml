import QtQuick
import "../geometry"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string mode: companionBridge ? companionBridge.stageMode : "presence"

    Rectangle {
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.82
        height: width
        radius: width / 2
        color: root.theme ? root.theme.paleCyan : "#B8CED9"
        opacity: 0.022 + (emotionBridge ? emotionBridge.presenceLevel * 0.035 : 0.018)
    }

    OrbitalField {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
        density: 0.70
    }

    Image {
        id: portrait
        source: appBridge ? appBridge.assetUrl("companionPortrait") : ""
        anchors.centerIn: parent
        width: Math.min(parent.width * 0.62, parent.height * 0.78)
        height: width * 1.18
        fillMode: Image.PreserveAspectFit
        opacity: status === Image.Ready ? 0.76 : 0
        asynchronous: true
    }

    Item {
        id: placeholder
        anchors.centerIn: parent
        width: Math.min(parent.width, parent.height) * 0.48
        height: width
        visible: portrait.opacity === 0
        Rectangle {
            anchors.centerIn: parent
            width: parent.width
            height: parent.height
            radius: width / 2
            color: root.theme ? root.theme.accent : "#D97855"
            opacity: 0.08
        }
        Rectangle {
            anchors.centerIn: parent
            width: parent.width * 0.22
            height: width
            radius: width / 2
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.66
        }
    }

    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 18
        text: companionBridge && companionBridge.live2dReady ? appBridge.t("companion.title", root.language) : appBridge.t("companion.stageHint", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.58
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeSmall : 12
    }
}
