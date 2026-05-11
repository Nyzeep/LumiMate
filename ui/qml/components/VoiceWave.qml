import QtQuick
import "../design_system"

Item {
    id: root
    Colors { id: colors }
    Motion { id: motion }
    property real activity: chatBridge ? chatBridge.voiceLevel : 0.0
    property string stage: chatBridge ? chatBridge.phase : "idle"
    property real drift: 0

    NumberAnimation on drift {
        from: 0
        to: Math.PI * 2
        duration: motion.breathDuration
        loops: Animation.Infinite
        running: root.visible
    }

    Canvas {
        id: wave
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d")
            ctx.clearRect(0, 0, width, height)

            var level = Math.max(0.10, root.activity + (root.stage === "listening" ? 0.22 : root.stage === "replying" ? 0.14 : 0.05))
            var mid = height / 2
            var amplitude = 4 + level * 10

            function drawLine(color, alpha, offset, multiplier) {
                ctx.beginPath()
                ctx.lineWidth = 1.4
                ctx.strokeStyle = color
                for (var x = 0; x <= width; x += 4) {
                    var theta = (x / width) * Math.PI * (2.4 + multiplier) + root.drift + offset
                    var y = mid + Math.sin(theta) * amplitude * (0.58 + multiplier * 0.18)
                    if (x === 0) {
                        ctx.moveTo(x, y)
                    } else {
                        ctx.lineTo(x, y)
                    }
                }
                ctx.globalAlpha = alpha
                ctx.stroke()
                ctx.globalAlpha = 1.0
            }

            drawLine("#F2C39B", 0.82, 0.0, 0.0)
            drawLine("#D1BBC0", 0.36, 0.8, 0.6)
            drawLine("#8E8A95", 0.22, 1.6, 0.2)
        }
    }

    onActivityChanged: wave.requestPaint()
    onStageChanged: wave.requestPaint()
    onDriftChanged: wave.requestPaint()
}
