import QtQuick
import "../pages"

Item {
    id: root
    property var theme
    property var motion
    property string language: "zh-CN"
    property string page: appBridge ? appBridge.currentPage : "home"

    HomeSpace {
        anchors.fill: parent
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "home"
    }
    ChatSpace {
        anchors.fill: parent
        anchors.margins: 34
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "chat"
    }
    CompanionSpace {
        anchors.fill: parent
        anchors.margins: 34
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "companion"
    }
    WorkbenchSpace {
        anchors.fill: parent
        anchors.margins: 34
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "workbench"
    }
    SettingsSpace {
        anchors.fill: parent
        anchors.margins: 34
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "settings"
    }
    AboutSpace {
        anchors.fill: parent
        anchors.margins: 34
        theme: root.theme
        motion: root.motion
        language: root.language
        active: root.page === "about"
    }
}
