import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }
    property string startupSelection: appBridge.startupPage
    property bool checkUpdates: appBridge.checkUpdateOnStartup
    property bool reduceMotion: appBridge.reduceMotion

    Text {
        x: 28
        y: 76
        text: appBridge.t("settings.title", appBridge.language)
        color: colors.neuralWhite
        font.family: typography.display(appBridge.language)
        font.pixelSize: typography.title
    }

    Text {
        x: 28
        y: 116
        width: root.width * 0.52
        text: appBridge.t("settings.subtitle", appBridge.language)
        wrapMode: Text.WordWrap
        color: colors.dimText
        font.family: typography.sans(appBridge.language)
        font.pixelSize: typography.body
    }

    Row {
        x: 28
        y: 182
        spacing: 18

        GlassPanel {
            width: root.width * 0.34
            height: 360

            Column {
                x: 20
                y: 18
                spacing: 12

                Text {
                    text: appBridge.t("settings.section.system", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    text: appBridge.t("settings.language", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Row {
                    spacing: 10
                    OrbitButton {
                        width: 150
                        label: appBridge.t("settings.lang.zh", appBridge.language)
                        subtitle: "zh-CN"
                        tier: appBridge.language === "zh-CN" ? "primary" : "tertiary"
                        onActivated: appBridge.setLanguage("zh-CN")
                    }
                    OrbitButton {
                        width: 150
                        label: appBridge.t("settings.lang.en", appBridge.language)
                        subtitle: "en-US"
                        tier: appBridge.language === "en-US" ? "primary" : "tertiary"
                        onActivated: appBridge.setLanguage("en-US")
                    }
                }

                Text {
                    text: appBridge.t("settings.startup_page", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Row {
                    spacing: 8
                    Repeater {
                        model: [
                            { id: "home", label: appBridge.t("settings.startup.home", appBridge.language) },
                            { id: "chat", label: appBridge.t("settings.startup.chat", appBridge.language) },
                            { id: "companion", label: appBridge.t("settings.startup.companion", appBridge.language) },
                            { id: "workbench", label: appBridge.t("settings.startup.workbench", appBridge.language) },
                            { id: "settings", label: appBridge.t("settings.startup.settings", appBridge.language) }
                        ]
                        OrbitButton {
                            width: 124
                            label: modelData.label
                            subtitle: modelData.id
                            tier: root.startupSelection === modelData.id ? "secondary" : "tertiary"
                            onActivated: root.startupSelection = modelData.id
                        }
                    }
                }

                Row {
                    spacing: 10
                    OrbitButton {
                        width: 160
                        label: appBridge.t("settings.update_on_start", appBridge.language)
                        subtitle: root.checkUpdates ? "On" : "Off"
                        tier: root.checkUpdates ? "secondary" : "tertiary"
                        onActivated: root.checkUpdates = !root.checkUpdates
                    }
                    OrbitButton {
                        width: 160
                        label: appBridge.t("settings.reduce_motion", appBridge.language)
                        subtitle: root.reduceMotion ? "On" : "Off"
                        tier: root.reduceMotion ? "secondary" : "tertiary"
                        onActivated: root.reduceMotion = !root.reduceMotion
                    }
                }

                OrbitButton {
                    width: 220
                    label: appBridge.t("settings.save", appBridge.language)
                    subtitle: appBridge.t("settings.saved", appBridge.language)
                    tier: "primary"
                    onActivated: appBridge.saveSettings(appBridge.language, root.checkUpdates, root.startupSelection, root.reduceMotion)
                }
            }
        }

        Column {
            spacing: 18

            GlassPanel {
                width: root.width * 0.24
                height: 168
                Column {
                    x: 18
                    y: 18
                    spacing: 8
                    Text {
                        text: appBridge.t("settings.section.storage", appBridge.language)
                        color: colors.neuralWhite
                        font.family: typography.display(appBridge.language)
                        font.pixelSize: typography.section
                    }
                    Text {
                        text: appBridge.t("settings.storage.used", appBridge.language)
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                    Text {
                        text: modelBridge.modelRoot
                        width: parent.width - 16
                        wrapMode: Text.WordWrap
                        color: colors.quietText
                        font.family: typography.mono
                        font.pixelSize: typography.small
                    }
                    Text {
                        width: parent.width - 16
                        text: appBridge.t("settings.storage.note", appBridge.language)
                        wrapMode: Text.WordWrap
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                }
            }

            GlassPanel {
                width: root.width * 0.24
                height: 174
                Column {
                    x: 18
                    y: 18
                    spacing: 8
                    Text {
                        text: appBridge.t("settings.section.about", appBridge.language)
                        color: colors.neuralWhite
                        font.family: typography.display(appBridge.language)
                        font.pixelSize: typography.section
                    }
                    Text {
                        text: appBridge.t("settings.about.runtime", appBridge.language) + ": Python + PySide6 + Qt Quick"
                        color: colors.quietText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.body
                    }
                    Text {
                        text: appBridge.t("settings.about.version", appBridge.language) + ": " + appBridge.appVersion
                        color: colors.quietText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.body
                    }
                    Text {
                        text: appBridge.t("settings.about.author", appBridge.language) + ": " + appBridge.appAuthor
                        color: colors.quietText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.body
                    }
                    Text {
                        text: appBridge.t("settings.about.update", appBridge.language) + ": " + appBridge.updateSource
                        width: parent.width - 16
                        wrapMode: Text.WordWrap
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                }
            }
        }
    }
}
