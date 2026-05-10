import QtQuick

QtObject {
    readonly property color inkDeep: "#020713"
    readonly property color ink: "#071120"
    readonly property color midnight: "#0B1628"
    readonly property color twilight: "#10203A"
    readonly property color panel: "#101B31"
    readonly property color panelSoft: "#15213A"
    readonly property color moon: "#F2C7B5"
    readonly property color moonPale: "#F7D9CA"
    readonly property color text: "#F2EDE5"
    readonly property color textWarm: "#F4D4C3"
    readonly property color muted: "#AEB8C3"
    readonly property color dim: "#788798"
    readonly property color accent: "#D97855"
    readonly property color accentSoft: "#F1A47A"
    readonly property color paleCyan: "#B8CED9"
    readonly property color mistBlue: "#82A6BF"
    readonly property color line: "#C9D9E2"

    readonly property real hairline: 1
    readonly property real ringLine: 1.05
    readonly property real panelOpacity: 0.30
    readonly property real quietOpacity: 0.62
    readonly property real glowOpacity: 0.20
    readonly property real particleDensity: 0.66

    readonly property int radiusTiny: 8
    readonly property int radiusSoft: 18
    readonly property int radiusLarge: 28
    readonly property int radiusCard: 22
    readonly property int spaceXs: 8
    readonly property int spaceSm: 12
    readonly property int spaceMd: 18
    readonly property int spaceLg: 28
    readonly property int spaceXl: 44

    readonly property string sansFontZh: "Microsoft YaHei UI"
    readonly property string sansFontEn: "Segoe UI"
    readonly property string displayFontZh: "SimSun"
    readonly property string displayFontEn: "Georgia"
    readonly property string monoFont: "Consolas"
    readonly property string fontFamily: sansFontZh

    readonly property int typeBrand: 18
    readonly property int typeNav: 13
    readonly property int typeTime: 24
    readonly property int typeHero: 58
    readonly property int typeHeroSub: 19
    readonly property int typeTitle: 32
    readonly property int typeCardTitle: 18
    readonly property int typeCardValue: 30
    readonly property int typeBody: 14
    readonly property int typeSmall: 12

    function sans(language) {
        return language === "zh-CN" ? sansFontZh : sansFontEn
    }

    function display(language) {
        return language === "zh-CN" ? displayFontZh : displayFontEn
    }
}
