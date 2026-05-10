import QtQuick

QtObject {
    property bool reduceMotion: appBridge ? appBridge.reduceMotion : false
    readonly property real factor: reduceMotion ? 0.42 : 1.0
    readonly property int pageDuration: 1100 * factor
    readonly property int hoverDuration: 320 * factor
    readonly property int slowDriftDuration: 32000 * factor
    readonly property int orbitDuration: 24000 * factor
    readonly property int breathDuration: 5200 * factor
    readonly property int pulseDuration: 1900 * factor
}
