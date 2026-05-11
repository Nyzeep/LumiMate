import QtQuick
import "../components"
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    function percentText(value) {
        return Math.round(Math.max(0, Math.min(1, value)) * 100) + "%"
    }

    function phaseLabel() {
        return appBridge.t("state." + chatBridge.phase, appBridge.language)
    }

    function scrollToEnd() {
        scroll.contentY = Math.max(0, scroll.contentHeight - scroll.height)
    }

    function sendCurrentText() {
        var value = String(composer.text).trim()
        if (!value.length) {
            return
        }
        chatBridge.sendText(value)
        composer.text = ""
        composer.forceActiveFocus()
    }

    Connections {
        target: chatBridge

        function onMessagesChanged() {
            Qt.callLater(root.scrollToEnd)
        }
    }

    Component.onCompleted: Qt.callLater(root.scrollToEnd)

    SceneTitleBlock {
        id: titleBlock
        x: 0
        y: 0
        widthHint: 680
        numberLabel: appBridge.t("scene.chat.title", appBridge.language)
        titleEn: "Chat Space"
        subtitle: appBridge.t("scene.chat.subtitle", appBridge.language)
    }

    GlassPanel {
        x: 0
        y: 124
        width: root.width * 0.23
        height: root.height * 0.56

        Column {
            anchors.fill: parent
            spacing: 16

            Row {
                spacing: 10

                HaloIconButton {
                    diameter: 34
                    symbol: "\u2726"
                    active: true
                    clickable: false
                }

                Column {
                    spacing: 4

                    Text {
                        text: "Lumi"
                        color: colors.neuralWhite
                        font.family: typography.display(appBridge.language)
                        font.pixelSize: typography.section
                    }

                    Text {
                        text: appBridge.t("chat.presence.label", appBridge.language)
                        color: colors.dimText
                        font.family: typography.sans(appBridge.language)
                        font.pixelSize: typography.small
                    }
                }
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("chat.phase", appBridge.language)
                value: root.phaseLabel()
                detail: chatBridge.status
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("chat.voice.label", appBridge.language)
                value: root.percentText(chatBridge.voiceLevel)
                detail: appBridge.t("chat.voice.detail", appBridge.language)
                progress: chatBridge.voiceLevel
            }

            MetricLine {
                width: parent.width
                label: appBridge.t("chat.transcript", appBridge.language)
                value: String(chatBridge.messageCount)
                detail: appBridge.t("chat.transcript.detail", appBridge.language)
            }

            Text {
                width: parent.width
                visible: !modelBridge.loaded
                text: appBridge.t("chat.ready.hint", appBridge.language)
                wrapMode: Text.WordWrap
                color: colors.softAmber
                lineHeight: 1.35
                font.family: typography.sans(appBridge.language)
                font.pixelSize: typography.body
            }
        }
    }

    GlassPanel {
        id: conversationPanel
        x: root.width * 0.27
        y: 100
        width: root.width * 0.69
        height: root.height * 0.58
        tone: "soft"
        glowOpacity: 0.08

        Flickable {
            id: scroll
            anchors.fill: parent
            clip: true
            contentWidth: width
            contentHeight: transcriptColumn.height

            Column {
                id: transcriptColumn
                width: scroll.width - 4
                spacing: 18

                Item {
                    visible: chatBridge.messageCount === 0
                    width: parent.width
                    height: placeholderColumn.implicitHeight

                    Column {
                        id: placeholderColumn
                        width: parent.width * 0.72
                        spacing: 12

                        MessageOrbit {
                            width: parent.width
                            role: "assistant"
                            author: "Lumi"
                            body: appBridge.t("chat.message.empty.body", appBridge.language)
                        }

                        Text {
                            width: parent.width
                            text: appBridge.t("chat.message.empty.note", appBridge.language)
                            wrapMode: Text.WordWrap
                            color: colors.dimText
                            lineHeight: 1.35
                            font.family: typography.sans(appBridge.language)
                            font.pixelSize: typography.small
                        }
                    }
                }

                Repeater {
                    model: chatBridge.messages

                    MessageOrbit {
                        width: transcriptColumn.width
                        role: modelData.role
                        author: modelData.author
                        body: modelData.body
                    }
                }
            }
        }
    }

    Row {
        x: 0
        y: root.height - 118
        spacing: 14

        OrbitButton {
            width: 182
            label: appBridge.t("chat.action.listen", appBridge.language)
            subtitle: appBridge.t("chat.action.listen.sub", appBridge.language)
            tier: "secondary"
            active: chatBridge.running
            symbol: "\u25CE"
            onActivated: chatBridge.startVoice()
        }

        OrbitButton {
            width: 182
            label: appBridge.t("chat.action.stop", appBridge.language)
            subtitle: appBridge.t("chat.action.stop.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25CB"
            onActivated: chatBridge.stopVoice()
        }

        OrbitButton {
            width: 182
            label: appBridge.t("chat.action.clear", appBridge.language)
            subtitle: appBridge.t("chat.action.clear.sub", appBridge.language)
            tier: "tertiary"
            symbol: "\u25C7"
            onActivated: chatBridge.clear()
        }
    }

    GlassPanel {
        id: dock
        x: root.width * 0.27
        y: root.height - 120
        width: root.width * 0.69
        height: 88
        tone: "strong"
        radius: 34
        padding: 0
        glowOpacity: 0.12

        SpatialInput {
            id: composer
            x: 16
            y: 15
            width: dock.width * 0.50
            height: 58
            leadingSymbol: "\u25CE"
            placeholderText: appBridge.t("chat.placeholder", appBridge.language)
            onAccepted: root.sendCurrentText()
        }

        VoiceWave {
            x: composer.x + composer.width + 18
            anchors.verticalCenter: composer.verticalCenter
            width: dock.width * 0.18
            height: 34
        }

        Text {
            x: dock.width * 0.76
            anchors.verticalCenter: composer.verticalCenter
            text: root.phaseLabel()
            color: colors.dimText
            font.family: typography.sans(appBridge.language)
            font.pixelSize: typography.small
        }

        HaloIconButton {
            anchors.right: parent.right
            anchors.rightMargin: 18
            anchors.verticalCenter: composer.verticalCenter
            diameter: 38
            symbol: "\u25B3"
            active: true
            onActivated: root.sendCurrentText()
        }
    }
}
