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
        numberLabel: appBridge.t("scene.about.title", appBridge.language)
        titleEn: "About Lumi"
        subtitle: appBridge.t("scene.about.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 120
        width: root.width * 0.32
        height: root.height * 0.60
        tone: "strong"

        Column {
            anchors.fill: parent
            spacing: 14

            Text {
                text: appBridge.t("nav.brand", appBridge.language)
                color: colors.neuralWhite
                font.family: typography.display(appBridge.language)
                font.pixelSize: typography.hero
            }

            Text {
                width: parent.width
                text: appBridge.appPhilosophy
                wrapMode: Text.WordWrap
                color: colors.quietText
                lineHeight: 1.4
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("about.metric.version", appBridge.language)
                value: appBridge.appVersion
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("about.metric.author", appBridge.language)
                value: appBridge.appAuthor
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("about.metric.runtime", appBridge.language)
                value: "Python + PySide6 + Qt Quick"
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("about.metric.update", appBridge.language)
                value: appBridge.updateSource
            }
        }
    }

    Item {
        x: root.width * 0.38
        y: 94
        width: root.width * 0.56
        height: root.height * 0.64

        AmbientGlow {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenterOffset: parent.width * 0.18
            anchors.verticalCenterOffset: parent.height * 0.18
            width: parent.width * 0.48
            height: width
            glowColor: colors.nebulaGold
            glowOpacity: 0.18
        }

        Repeater {
            model: 5

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                anchors.horizontalCenterOffset: parent.width * 0.18
                anchors.verticalCenterOffset: parent.height * 0.18
                width: parent.width * (0.18 + index * 0.08)
                height: width
                radius: width / 2
                color: "transparent"
                border.width: index === 0 ? 2 : 1
                border.color: index === 0 ? Qt.rgba(0.95, 0.78, 0.63, 0.32) : Qt.rgba(0.62, 0.69, 0.82, 0.10)
            }
        }

        HeroCore {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.horizontalCenterOffset: parent.width * 0.18
            anchors.verticalCenterOffset: parent.height * 0.18
            coreDiameter: 134
            symbol: "\u2609"
            label: appBridge.t("about.core.label", appBridge.language)
            subtitle: appBridge.t("about.core.subtitle", appBridge.language)
            pulseLevel: 0.42
            onActivated: appBridge.navigate("home")
        }
    }

    GlassPanel {
        x: 0
        y: root.height - 150
        width: root.width * 0.94
        height: 118

        Row {
            spacing: 24

            Column {
                width: root.width * 0.36
                spacing: 8

                Text {
                    text: appBridge.t("about.metric.project", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Text {
                    width: parent.width
                    text: appBridge.projectRoot
                    wrapMode: Text.WrapAnywhere
                    color: colors.neuralWhite
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }

                Text {
                    width: parent.width
                    text: appBridge.t("about.quote", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    lineHeight: 1.35
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }
            }

            Column {
                width: root.width * 0.30
                spacing: 8

                Text {
                    text: appBridge.t("about.metric.python", appBridge.language)
                    color: colors.dimText
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }

                Text {
                    width: parent.width
                    text: appBridge.pythonExecutable
                    wrapMode: Text.WrapAnywhere
                    color: colors.neuralWhite
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.body
                }

                Text {
                    width: parent.width
                    text: appBridge.t("about.metric.python.detail", appBridge.language)
                    wrapMode: Text.WordWrap
                    color: colors.quietText
                    lineHeight: 1.35
                    font.family: typography.sans(appBridge.language)
                    font.pixelSize: typography.small
                }
            }
        }
    }
}
