import QtQuick

QtObject {
    readonly property int hoverDuration: 780
    readonly property int pageDuration: 1200
    readonly property int breathDuration: 6200
    readonly property int slowOrbitDuration: 28000
    readonly property int deepOrbitDuration: 52000
    readonly property int particleDuration: 24000
    readonly property var softEase: Easing.OutCubic
    readonly property var spatialEase: Easing.InOutSine
}
