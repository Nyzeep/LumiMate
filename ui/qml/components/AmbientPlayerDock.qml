import QtQuick

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"

    width: 456
    height: 70

    Rectangle {
        anchors.fill: parent
        radius: 32
        color: root.theme ? root.theme.panelSoft : "#15213A"
        opacity: 0.54
        border.width: 1
        border.color: Qt.rgba(0.79, 0.85, 0.89, 0.15)
    }

    Rectangle {
        x: 20
        anchors.verticalCenter: parent.verticalCenter
        width: 42
        height: 42
        radius: 21
        color: root.theme ? root.theme.accent : "#D97855"
        opacity: 0.16
        border.width: 1
        border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
        Rectangle {
            anchors.centerIn: parent
            width: 10
            height: 10
            radius: 5
            color: root.theme ? root.theme.moon : "#F3E1CE"
            opacity: 0.62
        }
    }

    Column {
        x: 78
        anchors.verticalCenter: parent.verticalCenter
        spacing: 3
        Text {
            text: appBridge.t("home.player.title", root.language)
            color: root.theme ? root.theme.text : "#F2EDE5"
            opacity: 0.86
            font.family: root.theme ? root.theme.display(root.language) : "SimSun"
            font.pixelSize: 17
        }
        Text {
            text: appBridge.t("home.player.subtitle", root.language)
            color: root.theme ? root.theme.muted : "#AEB8C3"
            opacity: 0.56
            font.family: root.theme ? root.theme.sans(root.language) : "Microsoft YaHei UI"
            font.pixelSize: 12
        }
    }

    Canvas {
        id: wave
        x: 220
        y: 20
        width: 142
        height: 30
        opacity: 0.48
        property real phase: 0
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)
            ctx.lineWidth = 1.2
            ctx.strokeStyle = "rgba(241,164,122,0.72)"
            ctx.beginPath()
            for (var i = 0; i < width; i++) {
                var y = height / 2 + Math.sin((i / width) * Math.PI * 6 + phase) * (3 + i / width * 7)
                if (i === 0) ctx.moveTo(i, y)
                else ctx.lineTo(i, y)
            }
            ctx.stroke()
            ctx.strokeStyle = "rgba(184,206,217,0.24)"
            ctx.beginPath()
            for (var j = 0; j < width; j++) {
                var yy = height / 2 + Math.sin((j / width) * Math.PI * 5 + phase * 0.7) * 4
                if (j === 0) ctx.moveTo(j, yy)
                else ctx.lineTo(j, yy)
            }
            ctx.stroke()
        }
        NumberAnimation on phase {
            from: 0
            to: 6.283
            duration: 15000
            loops: Animation.Infinite
            running: true
            onRunningChanged: wave.requestPaint()
        }
        onPhaseChanged: requestPaint()
    }

    Rectangle {
        anchors.right: parent.right
        anchors.rightMargin: 18
        anchors.verticalCenter: parent.verticalCenter
        width: 44
        height: 44
        radius: 22
        color: root.theme ? root.theme.accent : "#D97855"
        opacity: playHit.containsMouse ? 0.32 : 0.18
        border.width: 1
        border.color: root.theme ? root.theme.accentSoft : "#F1A47A"
        Text {
            anchors.centerIn: parent
            text: "▶"
            color: root.theme ? root.theme.moon : "#F3E1CE"
            font.pixelSize: 16
        }
        MouseArea {
            id: playHit
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
        }
    }
}
