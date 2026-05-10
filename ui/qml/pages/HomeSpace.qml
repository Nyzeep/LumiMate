import QtQuick
import "../components"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property bool active: false
    property var now: new Date()
    property bool compact: width < 1030

    visible: opacity > 0.01
    opacity: active ? 1 : 0
    scale: active ? 1 : 0.985

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

    Timer {
        interval: 60000
        running: true
        repeat: true
        onTriggered: root.now = new Date()
    }

    function weekdayText() {
        var day = root.now.getDay()
        if (root.language === "zh-CN") {
            return ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"][day]
        }
        return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][day]
    }

    function dateText() {
        if (root.language === "zh-CN") {
            return Qt.formatDate(root.now, "M月d日") + "  " + weekdayText()
        }
        return Qt.formatDate(root.now, "MMM d") + "  " + weekdayText()
    }

    Rectangle {
        x: 0
        y: 0
        width: 1
        height: parent.height
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.08
    }

    Repeater {
        model: 30
        Rectangle {
            width: 1 + (index % 3)
            height: width
            radius: width / 2
            x: root.width * (((index * 31) % 100) / 100)
            y: root.height * (((index * 47) % 100) / 100)
            color: index % 4 === 0 ? (root.theme ? root.theme.accentSoft : "#F1A47A") : (root.theme ? root.theme.paleCyan : "#B8CED9")
            opacity: 0.12 + (index % 5) * 0.025
        }
    }

    Column {
        id: headline
        x: 50
        y: 106
        width: compact ? parent.width * 0.58 : parent.width * 0.38
        spacing: 13

        Row {
            spacing: 11
            Text {
                text: Qt.formatTime(root.now, "hh:mm")
                color: root.theme ? root.theme.textWarm : "#F4D4C3"
                opacity: 0.88
                font.family: root.theme ? root.theme.display(root.language) : "SimSun"
                font.pixelSize: root.theme ? root.theme.typeTime : 24
            }
            Text {
                text: "☾"
                y: 4
                color: root.theme ? root.theme.moon : "#F3E1CE"
                opacity: 0.76
                font.pixelSize: 18
            }
        }

        Text {
            text: dateText()
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.72
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: root.theme ? root.theme.typeBody : 14
        }

        Item { width: 1; height: 22 }

        Text {
            text: appBridge.t("home.timePrefix", root.language) + (root.language === "zh-CN" ? "，" : ", ") + appBridge.t("nav.profile.name", root.language)
            width: parent.width
            color: root.theme ? root.theme.textWarm : "#F4D4C3"
            opacity: 0.96
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: root.theme ? root.theme.typeHero : 58
            lineHeight: 1.06
            wrapMode: Text.WordWrap
        }

        Text {
            text: appBridge.t("home.subtitle", root.language)
            width: parent.width
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.74
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: root.theme ? root.theme.typeHeroSub : 19
        }
    }

    LunarGateStage {
        x: compact ? parent.width * 0.30 : parent.width * 0.28
        y: compact ? parent.height * 0.15 : parent.height * 0.07
        width: compact ? parent.width * 0.68 : parent.width * 0.47
        height: parent.height * 0.72
        theme: root.theme
        motion: root.motion
        language: root.language
        opacity: 0.96
    }

    Row {
        id: actions
        x: compact ? 38 : parent.width * 0.08
        y: parent.height - 166
        spacing: compact ? 4 : 36
        scale: compact ? 0.86 : 1
        transformOrigin: Item.Left

        ReferenceActionNode {
            theme: root.theme
            motion: root.motion
            language: root.language
            title: appBridge.t("home.action.chat", root.language)
            subtitle: appBridge.t("home.action.chat.sub", root.language)
            glyph: "✦"
            onActivated: appBridge.navigate("chat")
        }
        ReferenceActionNode {
            theme: root.theme
            motion: root.motion
            language: root.language
            title: appBridge.t("home.action.companion", root.language)
            subtitle: appBridge.t("home.action.companion.sub", root.language)
            glyph: "⌂"
            onActivated: appBridge.navigate("companion")
        }
        ReferenceActionNode {
            theme: root.theme
            motion: root.motion
            language: root.language
            title: appBridge.t("home.action.workbench", root.language)
            subtitle: appBridge.t("home.action.workbench.sub", root.language)
            glyph: "△"
            onActivated: appBridge.navigate("workbench")
        }
    }

    Column {
        id: rightPanel
        visible: !compact
        opacity: compact ? 0 : 1
        x: parent.width - width - 38
        y: 96
        width: Math.min(456, parent.width * 0.34)
        spacing: 22

        StatusOrbitCard {
            width: parent.width
            theme: root.theme
            motion: root.motion
            language: root.language
        }

        MemoryPanel {
            width: parent.width
            theme: root.theme
            language: root.language
        }

        AmbientPlayerDock {
            width: parent.width
            theme: root.theme
            motion: root.motion
            language: root.language
        }
    }
}
