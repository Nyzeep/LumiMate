import QtQuick
import "../components"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property bool active: false
    property string selectedLanguage: appBridge ? appBridge.language : "zh-CN"
    property string startupPage: appBridge ? appBridge.startupPage : "home"
    property bool updateOnStart: appBridge ? appBridge.checkUpdateOnStartup : false
    property string feedback: ""

    visible: opacity > 0.01
    opacity: active ? 1 : 0
    scale: active ? 1 : 0.97

    Behavior on opacity { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }
    Behavior on scale { NumberAnimation { duration: root.motion ? root.motion.pageDuration : 1200; easing.type: Easing.InOutSine } }

    Connections {
        target: appBridge
        function onLanguageChanged() {
            root.selectedLanguage = appBridge.language
        }
        function onSettingsChanged() {
            root.startupPage = appBridge.startupPage
            root.updateOnStart = appBridge.checkUpdateOnStartup
        }
    }

    Text {
        x: 30
        y: 28
        text: appBridge.t("settings.title", root.language)
        color: root.theme ? root.theme.textWarm : "#F4D4C3"
        opacity: 0.92
        font.family: root.theme ? root.theme.display(root.language) : "SimSun"
        font.pixelSize: root.theme ? root.theme.typeTitle : 32
        font.weight: Font.DemiBold
    }

    Text {
        x: 32
        y: 76
        width: Math.min(parent.width * 0.62, 560)
        text: appBridge.t("settings.subtitle", root.language)
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.66
        font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
        font.pixelSize: root.theme ? root.theme.typeBody : 14
        wrapMode: Text.WordWrap
    }

    Rectangle {
        x: 32
        y: 128
        width: Math.min(parent.width - 64, 980)
        height: 1
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: 0.10
    }

    Column {
        id: languageColumn
        x: 34
        y: 166
        width: Math.min(parent.width * 0.42, 420)
        spacing: 12

        Text {
            text: appBridge.t("settings.language", root.language)
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.72
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: root.theme ? root.theme.typeCardTitle : 18
        }

        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.lang.zh", root.language)
            subtitle: root.selectedLanguage === "zh-CN" ? appBridge.t("settings.active", root.language) : appBridge.t("settings.language_option", root.language)
            width: parent.width
            onActivated: {
                root.selectedLanguage = "zh-CN"
                appBridge.setLanguage("zh-CN")
            }
        }
        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.lang.en", root.language)
            subtitle: root.selectedLanguage === "en-US" ? appBridge.t("settings.active", root.language) : appBridge.t("settings.language_option", root.language)
            width: parent.width
            onActivated: {
                root.selectedLanguage = "en-US"
                appBridge.setLanguage("en-US")
            }
        }
        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.update_on_start", root.language)
            subtitle: root.updateOnStart ? appBridge.t("settings.update.on", root.language) : appBridge.t("settings.update.off", root.language)
            width: parent.width
            onActivated: root.updateOnStart = !root.updateOnStart
        }
    }

    Column {
        id: startupColumn
        x: Math.max(languageColumn.x + languageColumn.width + 80, parent.width * 0.53)
        y: 166
        width: Math.min(parent.width - x - 44, 360)
        spacing: 12

        Text {
            text: appBridge.t("settings.startup_page", root.language)
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.72
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: root.theme ? root.theme.typeCardTitle : 18
        }

        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.startup.home", root.language)
            subtitle: root.startupPage === "home" ? appBridge.t("settings.startup.current", root.language) : appBridge.t("nav.home", root.language)
            width: parent.width
            onActivated: root.startupPage = "home"
        }
        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.startup.chat", root.language)
            subtitle: root.startupPage === "chat" ? appBridge.t("settings.startup.current", root.language) : appBridge.t("nav.chat", root.language)
            width: parent.width
            onActivated: root.startupPage = "chat"
        }
        OrbitNodeButton {
            theme: root.theme
            motion: root.motion
            label: appBridge.t("settings.startup.workbench", root.language)
            subtitle: root.startupPage === "workbench" ? appBridge.t("settings.startup.current", root.language) : appBridge.t("nav.workbench", root.language)
            width: parent.width
            onActivated: root.startupPage = "workbench"
        }
    }

    OrbitNodeButton {
        x: 34
        y: parent.height - 116
        width: Math.min(360, parent.width * 0.42)
        theme: root.theme
        motion: root.motion
        label: appBridge.t("settings.save", root.language)
        subtitle: root.feedback.length > 0 ? root.feedback : appBridge.t("settings.rhythm", root.language)
        onActivated: {
            appBridge.saveSettings(root.selectedLanguage, root.updateOnStart, root.startupPage)
            root.feedback = appBridge.t("settings.saved", root.language)
        }
    }
}
