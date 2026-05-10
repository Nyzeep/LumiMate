import QtQuick

Item {
    id: root
    property alias text: input.text
    property string placeholder: ""
    property var theme
    property var motion
    signal accepted(string text)

    height: 48
    implicitWidth: 360

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        height: 1
        color: root.theme ? root.theme.line : "#C9D9E2"
        opacity: input.activeFocus ? 0.42 : 0.18
    }

    Rectangle {
        width: 13
        height: 13
        radius: 7
        anchors.left: parent.left
        anchors.verticalCenter: parent.verticalCenter
        color: root.theme ? root.theme.accentSoft : "#F1A47A"
        opacity: input.activeFocus ? 0.82 : 0.38
    }

    TextInput {
        id: input
        anchors.left: parent.left
        anchors.leftMargin: 28
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        height: parent.height
        color: root.theme ? root.theme.text : "#F2EDE5"
        selectionColor: root.theme ? root.theme.accent : "#D97855"
        font.family: root.theme ? root.theme.fontFamily : "Segoe UI"
        font.pixelSize: 14
        verticalAlignment: TextInput.AlignVCenter
        clip: true
        onAccepted: root.accepted(text)
    }

    Text {
        anchors.left: input.left
        anchors.verticalCenter: parent.verticalCenter
        text: root.placeholder
        visible: input.text.length === 0 && !input.activeFocus
        color: root.theme ? root.theme.muted : "#AEB8C3"
        opacity: 0.46
        font.family: root.theme ? root.theme.fontFamily : "Segoe UI"
        font.pixelSize: 13
    }
}
