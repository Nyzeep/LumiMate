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

    function onOffLabel(value) {
        return value ? appBridge.t("common.on", appBridge.language) : appBridge.t("common.off", appBridge.language)
    }

    function sceneLabel(sceneId) {
        return appBridge.t("nav." + sceneId, appBridge.language)
    }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 680
        numberLabel: appBridge.t("scene.settings.title", appBridge.language)
        titleEn: "Settings"
        subtitle: appBridge.t("scene.settings.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 120
        width: root.width * 0.66
        height: root.height * 0.66
        tone: "soft"

        Flickable {
            anchors.fill: parent
            clip: true
            contentWidth: width
            contentHeight: settingsColumn.height

            Column {
                id: settingsColumn
                width: parent.width
                spacing: 18

                Text {
                    text: appBridge.t("settings.section.system", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.title
                }

                Text {
                    text: appBridge.t("settings.language", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Row {
                    spacing: 12

                    OrbitButton {
                        width: 196
                        label: appBridge.t("settings.lang.zh", appBridge.language)
                        subtitle: "zh-CN"
                        tier: appBridge.language === "zh-CN" ? "primary" : "tertiary"
                        symbol: "\u25CE"
                        onActivated: appBridge.setLanguage("zh-CN")
                    }

                    OrbitButton {
                        width: 196
                        label: appBridge.t("settings.lang.en", appBridge.language)
                        subtitle: "en-US"
                        tier: appBridge.language === "en-US" ? "primary" : "tertiary"
                        symbol: "\u25C8"
                        onActivated: appBridge.setLanguage("en-US")
                    }
                }

                Text {
                    text: appBridge.t("settings.startup_page", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Repeater {
                    model: appBridge.sceneGroups

                    Column {
                        width: settingsColumn.width
                        spacing: 10

                        Text {
                            text: appBridge.t(modelData.labelKey, appBridge.language)
                            color: colors.softAmber
                            font.family: typography.display(appBridge.language)
                            font.pixelSize: typography.section
                        }

                        Row {
                            spacing: 10

                            Repeater {
                                model: modelData.scenes

                                OrbitButton {
                                    width: 164
                                    label: appBridge.t(modelData.labelKey, appBridge.language)
                                    subtitle: modelData.id
                                    tier: root.startupSelection === modelData.id ? "secondary" : "tertiary"
                                    symbol: modelData.icon
                                    onActivated: root.startupSelection = modelData.id
                                }
                            }
                        }
                    }
                }

                Row {
                    spacing: 12

                    OrbitButton {
                        width: 220
                        label: appBridge.t("settings.update_on_start", appBridge.language)
                        subtitle: root.onOffLabel(root.checkUpdates)
                        tier: root.checkUpdates ? "secondary" : "tertiary"
                        symbol: "\u25CE"
                        onActivated: root.checkUpdates = !root.checkUpdates
                    }

                    OrbitButton {
                        width: 220
                        label: appBridge.t("settings.reduce_motion", appBridge.language)
                        subtitle: root.onOffLabel(root.reduceMotion)
                        tier: root.reduceMotion ? "secondary" : "tertiary"
                        symbol: "\u25CB"
                        onActivated: root.reduceMotion = !root.reduceMotion
                    }
                }

                OrbitButton {
                    width: 220
                    label: appBridge.t("settings.save", appBridge.language)
                    subtitle: appBridge.t("settings.saved", appBridge.language)
                    tier: "primary"
                    symbol: "\u25B3"
                    onActivated: appBridge.saveSettings(appBridge.language, root.checkUpdates, root.startupSelection, root.reduceMotion)
                }
            }
        }
    }

    Column {
        x: root.width * 0.71
        y: 120
        spacing: 18

        GlassPanel {
            width: root.width * 0.25
            height: 244
            tone: "strong"

            Column {
                anchors.fill: parent
                spacing: 16

                Text {
                    text: appBridge.t("settings.summary.title", appBridge.language)
                    color: colors.neuralWhite
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("settings.summary.language", appBridge.language)
                    value: appBridge.language
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("settings.summary.startup", appBridge.language)
                    value: root.sceneLabel(root.startupSelection)
                    detail: root.startupSelection
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("settings.summary.motion", appBridge.language)
                    value: root.onOffLabel(root.reduceMotion)
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("settings.summary.update", appBridge.language)
                    value: root.onOffLabel(root.checkUpdates)
                }
            }
        }

        GlassPanel {
            width: root.width * 0.25
            height: 184

            Column {
                anchors.fill: parent
                spacing: 10

                Text {
                    text: appBridge.t("settings.note.title", appBridge.language)
                    color: colors.softAmber
                    font.family: typography.display(appBridge.language)
                    font.pixelSize: typography.section
                }

                Text {
                    width: parent.width
                    text: appBridge.t("settings.note.body", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    lineHeight: 1.4
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }
            }
        }
    }
}
