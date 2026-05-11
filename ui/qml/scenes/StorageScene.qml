import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 640
        numberLabel: appBridge.t("scene.storage.title", appBridge.language)
        titleEn: "Storage"
        subtitle: appBridge.t("scene.storage.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 120
        width: root.width * 0.34
        height: root.height * 0.60
        tone: "strong"

        Item {
            anchors.fill: parent

            AmbientGlow {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 18
                width: parent.width * 0.84
                height: width
                glowColor: colors.nebulaGold
                glowOpacity: 0.18
            }

            Repeater {
                model: 5

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    y: 28 + index * 18
                    width: parent.width * (0.30 + index * 0.10)
                    height: width
                    radius: width / 2
                    color: "transparent"
                    border.width: index === 0 ? 2 : 1
                    border.color: index === 0 ? Qt.rgba(0.95, 0.78, 0.63, 0.34) : Qt.rgba(0.62, 0.69, 0.82, 0.12)
                }
            }

            HaloIconButton {
                anchors.horizontalCenter: parent.horizontalCenter
                y: 110
                diameter: 66
                symbol: "\u2B22"
                active: true
                clickable: false
            }

            Column {
                x: 0
                y: 250
                width: parent.width
                spacing: 14

                MetricLine {
                    width: parent.width
                    label: appBridge.t("storage.metric.used", appBridge.language)
                    value: modelBridge.storageUsedLabel
                    detail: modelBridge.storageTotalLabel
                    progress: modelBridge.storageUsageRatio
                }

                MetricLine {
                    width: parent.width
                    label: appBridge.t("storage.metric.free", appBridge.language)
                    value: modelBridge.storageFreeLabel
                    detail: appBridge.t("storage.metric.free.detail", appBridge.language)
                }
            }
        }
    }

    GlassPanel {
        x: root.width * 0.39
        y: 120
        width: root.width * 0.55
        height: root.height * 0.60

        Column {
            anchors.fill: parent
            spacing: 14

            Text {
                text: appBridge.t("storage.metric.buckets", appBridge.language)
                color: colors.neuralWhite
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.title
            }

            Repeater {
                model: modelBridge.storageItems

                GlassPanel {
                    width: parent ? parent.width : 0
                    height: 84
                    tone: "soft"
                    padding: 16

                    Row {
                        anchors.fill: parent
                        spacing: 16

                        HaloIconButton {
                            anchors.verticalCenter: parent.verticalCenter
                            diameter: 34
                            symbol: index === 0 ? "\u25CE" : index === 1 ? "\u25C8" : index === 2 ? "\u2726" : index === 3 ? "\u25A1" : "\u2B22"
                            active: true
                            clickable: false
                        }

                        Column {
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 4

                            Text {
                                text: appBridge.t(modelData.titleKey, appBridge.language)
                                color: colors.neuralWhite
                                font.family: typography.display(appBridge.language)
                                font.pixelSize: typography.section
                            }

                            Text {
                                width: root.width * 0.34
                                text: modelData.path
                                color: colors.dimText
                                elide: Text.ElideMiddle
                                font.family: typography.mono
                                font.pixelSize: typography.small
                            }
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: modelData.valueLabel
                            color: colors.softAmber
                            font.family: typography.display("en-US")
                            font.pixelSize: typography.title
                        }
                    }
                }
            }
        }
    }

    GlassPanel {
        x: 0
        y: root.height - 158
        width: root.width * 0.46
        height: 126

        Column {
            anchors.fill: parent
            spacing: 10

            Text {
                text: appBridge.t("storage.protected.title", appBridge.language)
                color: colors.softAmber
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.section
            }

            Text {
                width: parent.width
                text: appBridge.t("storage.protected.body", appBridge.language)
                wrapMode: Text.WordWrap
                color: colors.quietText
                lineHeight: 1.35
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }
        }
    }

    Row {
        x: root.width * 0.52
        y: root.height - 150
        spacing: 12

        OrbitButton {
            width: 172
            label: appBridge.t("storage.action.scan", appBridge.language)
            subtitle: appBridge.t("storage.action.scan.sub", appBridge.language)
            tier: "secondary"
            symbol: "\u25CE"
            onActivated: modelBridge.scanModels()
        }

        OrbitButton {
            width: 172
            label: appBridge.t("storage.action.release", appBridge.language)
            subtitle: appBridge.t("storage.action.release.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25CB"
            onActivated: modelBridge.releaseCache()
        }

        OrbitButton {
            width: 172
            label: appBridge.t("storage.action.workbench", appBridge.language)
            subtitle: appBridge.t("storage.action.workbench.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25C8"
            onActivated: appBridge.navigate("workbench")
        }
    }
}
