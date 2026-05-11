import QtQuick
import QtQuick.Window
import "../design_system"

Row {
    id: root
    Colors { id: colors }
    property var windowRef
    spacing: 10

    Repeater {
        model: appBridge.sceneGroups

        HaloIconButton {
            diameter: 30
            symbol: String(index + 1)
            active: index === appBridge.currentSceneGroupIndex
            onActivated: appBridge.setSceneGroup(index)
        }
    }

    Item { width: 8; height: 1 }

    HaloIconButton {
        diameter: 28
        symbol: "—"
        onActivated: if (root.windowRef) root.windowRef.showMinimized()
    }

    HaloIconButton {
        diameter: 28
        symbol: root.windowRef && root.windowRef.visibility === Window.Maximized ? "❐" : "□"
        onActivated: {
            if (!root.windowRef) {
                return
            }
            if (root.windowRef.visibility === Window.Maximized) {
                root.windowRef.showNormal()
            } else {
                root.windowRef.showMaximized()
            }
        }
    }

    HaloIconButton {
        diameter: 28
        symbol: "×"
        onActivated: if (root.windowRef) root.windowRef.close()
    }
}
