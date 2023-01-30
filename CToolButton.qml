import QtQuick 2.14
import QtQuick.Controls 2.15

ToolButton {
    id: root

    property bool active: false
    property bool highlight: false

    antialiasing: true
    display: AbstractButton.IconOnly
    width: parent.width
    implicitWidth: implicitHeight
    implicitHeight: contentImage.height + root.padding * 2
    contentItem: Item {
        data: [
            Image {
                id: contentImage
                source: root.icon.source
                width: 24
                height: 24
                fillMode: Image.PreserveAspectFit
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                opacity: enabled ? 1 : 0.3
            }
        ]
    }
    background: Rectangle {
        id: backgroundRectangle
        color: root.down || root.checked || root.highlighted  ? root.palette.mid : root.palette.button
        opacity: enabled ? 1 : 0.3
    }
}
