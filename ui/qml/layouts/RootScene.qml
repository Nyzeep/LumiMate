import QtQuick
import "../animations"
import "../components"
import "../effects"
import "../themes"

Item {
    id: root
    property var windowRef
    property string language: appBridge ? appBridge.language : "zh-CN"

    Theme { id: theme }
    MotionRuntime { id: motion }

    DeepSpaceBackground {
        anchors.fill: parent
        theme: theme
        motion: motion
    }

    Repeater {
        model: [0.34, 0.62, 0.80]
        Rectangle {
            x: root.width * modelData
            y: 0
            width: 1
            height: root.height
            color: theme.line
            opacity: 0.06
        }
    }

    SpatialRouter {
        anchors.left: sideRail.right
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        theme: theme
        motion: motion
        language: root.language
    }

    ReferenceSideRail {
        id: sideRail
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        theme: theme
        motion: motion
        language: root.language
    }

    MouseArea {
        anchors.left: sideRail.right
        anchors.right: topControls.left
        anchors.top: parent.top
        height: 44
        acceptedButtons: Qt.LeftButton
        onPressed: {
            if (root.windowRef && root.windowRef.startSystemMove) {
                root.windowRef.startSystemMove()
            }
        }
    }

    TopWindowControls {
        id: topControls
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 24
        theme: theme
        motion: motion
        language: root.language
        windowRef: root.windowRef
    }
}
