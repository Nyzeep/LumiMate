import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property bool shaderAvailable: appBridge ? appBridge.assetExists("breathingNebulaShader") : false
    property real time: 0

    Timer {
        interval: 33
        running: true
        repeat: true
        onTriggered: root.time += 0.004
    }

    Loader {
        anchors.fill: parent
        active: root.shaderAvailable
        sourceComponent: ShaderEffect {
            property real t: root.time
            fragmentShader: appBridge ? appBridge.assetUrl("breathingNebulaShader") : ""
        }
    }

    Item {
        anchors.fill: parent
        visible: !root.shaderAvailable

        Rectangle {
            anchors.fill: parent
            color: root.theme ? root.theme.inkDeep : "#020713"
        }

        Rectangle {
            width: parent.width * 0.74
            height: width
            radius: width / 2
            x: parent.width * 0.52
            y: -height * 0.28
            color: root.theme ? root.theme.mistBlue : "#82A6BF"
            opacity: 0.035
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { to: 1.08; duration: root.motion ? root.motion.breathDuration : 6200; easing.type: Easing.InOutSine }
                NumberAnimation { to: 0.96; duration: root.motion ? root.motion.breathDuration : 6200; easing.type: Easing.InOutSine }
            }
        }

        Rectangle {
            width: parent.width * 0.54
            height: width
            radius: width / 2
            x: -width * 0.18
            y: parent.height * 0.42
            color: root.theme ? root.theme.accent : "#D97855"
            opacity: 0.032
            SequentialAnimation on scale {
                loops: Animation.Infinite
                NumberAnimation { to: 0.92; duration: 9000; easing.type: Easing.InOutSine }
                NumberAnimation { to: 1.08; duration: 9000; easing.type: Easing.InOutSine }
            }
        }
    }
}
