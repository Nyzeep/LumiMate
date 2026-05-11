import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Typography { id: typography }

    property string numberLabel: ""
    property string title: ""
    property string titleEn: ""
    property string subtitle: ""
    property int widthHint: 640

    implicitWidth: widthHint
    implicitHeight: block.implicitHeight

    Column {
        id: block
        width: root.widthHint
        spacing: 8

        Row {
            spacing: 10

            Text {
                id: mainTitle
                text: root.numberLabel
                color: colors.softAmber
                font.family: typography.display(appBridge ? appBridge.language : "zh-CN")
                font.pixelSize: typography.title
            }

            Text {
                text: root.titleEn ? "(" + root.titleEn + ")" : ""
                color: colors.dimText
                anchors.baseline: mainTitle.baseline
                font.family: typography.display("en-US")
                font.pixelSize: typography.section
            }
        }

        Text {
            width: parent.width
            text: root.subtitle
            color: colors.dimText
            wrapMode: Text.WordWrap
            font.family: typography.sans(appBridge ? appBridge.language : "zh-CN")
            font.pixelSize: typography.body
            lineHeight: 1.35
        }
    }
}
