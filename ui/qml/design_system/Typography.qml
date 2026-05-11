import QtQuick

QtObject {
    readonly property string sansZh: "Microsoft YaHei UI"
    readonly property string sansEn: "Segoe UI"
    readonly property string displayZh: sansZh
    readonly property string displayEn: sansEn
    readonly property string mono: "Consolas"

    readonly property int hero: 62
    readonly property int title: 30
    readonly property int section: 18
    readonly property int body: 14
    readonly property int small: 12
    readonly property int micro: 10
    readonly property int caption: 11

    function sans(language) {
        return language === "zh-CN" ? sansZh : sansEn
    }

    function display(language) {
        return language === "zh-CN" ? displayZh : displayEn
    }
}
