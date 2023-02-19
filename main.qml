import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import QtWebEngine 1.10
import Qt.labs.settings 1.1

ApplicationWindow {
    id: appRoot
    width: 1024
    height: 750
    visible: true

    property var favoriteNameList
    property var favoriteUrlList
    property int pastVisibility

    Settings {
        id: appSettings
        property alias width: appRoot.width
        property alias height: appRoot.height
    }

    Settings {
        id: appSettingsFavorite
        category: "Favorite"
        property var nameList
        property var urlList
    }

    Component.onCompleted: {
        favoriteNameList = appSettingsFavorite.nameList !== undefined ? appSettingsFavorite.nameList : []
        favoriteUrlList = appSettingsFavorite.urlList !== undefined ? appSettingsFavorite.urlList : []
    }

    Component.onDestruction: {
        appSettingsFavorite.nameList = favoriteNameList
        appSettingsFavorite.urlList = favoriteUrlList
    }

    header: ToolBar {
        id: headerToolBar
        RowLayout {
            anchors.fill: parent

            CToolButton {
                id: googleButton
                icon.source: "img/google.png"
                onClicked: webEngineView.url = "https://google.com/"
            }

            ToolButton {
                property int itemAction: WebEngineView.Back
                enabled: webEngineView.action(itemAction).enabled
                onClicked: webEngineView.action(itemAction).trigger()
                icon.name: webEngineView.action(itemAction).iconName
                display: AbstractButton.IconOnly
            }

            ToolButton {
                property int itemAction: WebEngineView.Forward
                enabled: webEngineView.action(itemAction).enabled
                onClicked: webEngineView.action(itemAction).trigger()
                icon.name: webEngineView.action(itemAction).iconName
                display: AbstractButton.IconOnly
            }

            ToolButton {
                property int itemAction: webEngineView.loading ? WebEngineView.Stop : WebEngineView.Reload
                enabled: webEngineView.action(itemAction).enabled
                onClicked: webEngineView.action(itemAction).trigger()
                icon.name: webEngineView.action(itemAction).iconName
                display: AbstractButton.IconOnly
            }

            TextField {
                id: urlTextField
                property string pastText

                Layout.fillWidth: true
                text: webEngineView.url
                selectByMouse: true
                color: activeFocus ? "#000" : "#555"
                onEditingFinished: {
                    if (text != pastText)
                        webEngineView.url = text
                    focus = false
                }
                onActiveFocusChanged: {
                    if (activeFocus) {
                        selectAll()
                        pastText = text
                    }
                }

                background: Rectangle {
                    radius: 2
                    implicitWidth: 100
                    implicitHeight: 24
                    border.color: parent.activeFocus ? "#21be2b" : "transparent"
                    border.width: 1
                }

            }

            CToolButton {
                id: favoriteButton
                checkable: true
                icon.source: checked ? "img/star_t.png" : "img/star_f.png"
                onClicked: {
                    if (checked) {
                        if (!favoriteUrlList.includes(webEngineView.url.toString())) {
                            favoriteNameList.push(webEngineView.title.toString())
                            favoriteUrlList.push(webEngineView.url.toString())
                            bookmarksMenuRepeater.model = favoriteNameList
                            if (!bookmarksButton.enabled)
                                bookmarksButton.enabled = true
                        }
                    }
                    else {
                        let index = favoriteUrlList.indexOf(webEngineView.url.toString())
                        if (index > -1) {
                            favoriteNameList.splice(index, 1)
                            favoriteUrlList.splice(index, 1)
                            bookmarksMenuRepeater.model = favoriteNameList
                            bookmarksButton.enabled = favoriteUrlList.length > 0
                        }
                    }
                }
                background: Rectangle {
                    color: favoriteButton.down ? favoriteButton.palette.mid : favoriteButton.palette.button
                }
            }


            CToolButton {
                id: bookmarksButton
                icon.source: "img/bookmarks.png"
                onClicked: bookmarksMenu.open()
                checked: bookmarksMenu.visible
                enabled: favoriteUrlList.length > 0

                Menu {
                    id: bookmarksMenu
                    y: bookmarksButton.height
                    Repeater {
                        id: bookmarksMenuRepeater
                        model: favoriteNameList
                        MenuItem {
                            text: favoriteNameList[index]
                            onClicked: {
                                webEngineView.url = favoriteUrlList[index]
                            }
                        }
                    }
                    background: Rectangle {
                        implicitWidth: 400
                        implicitHeight: 40
                        color: "#ffffff"
                        border.color: "#21be2b"
                        radius: 2
                    }
                }
            }
        }
    }

    footer: Rectangle {
        id: footerRectangle
        implicitWidth: 100
        implicitHeight: 30
        color: "#e6e6e6"
        visible: false

        ProgressBar {
            id: progressBar
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            from: 0
            to: 100
            background: Rectangle {
                implicitWidth: 200
                implicitHeight: 6
                color: "#e6e6e6"
            }
            contentItem: Rectangle {
                width: progressBar.visualPosition * parent.width
                color: "#21be2b"
            }
        }

        Label {
            id: footerLogLabel
            anchors.top: progressBar.bottom
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
        }
    }

    WebEngineView {
        id: webEngineView
        anchors.fill: parent
        url: "https://www.google.com/"

        onLoadingChanged: {
            switch (loadRequest.status) {
            case WebEngineView.LoadStartedStatus:
                footerRectangle.visible = true;
                favoriteButton.enabled = false
                break;
            case WebEngineView.LoadStoppedStatus:
            case WebEngineView.LoadSucceededStatus:
                appRoot.title = "%1 | %2".arg(appName).arg(title)
                if (favoriteUrlList.includes(url.toString()))
                    favoriteButton.checked = true
                else
                    favoriteButton.checked = false
                favoriteButton.enabled = true
                progressBarTimer.start()
                break;
            case WebEngineView.LoadFailedStatus:
                break;
            }
        }
        onLoadProgressChanged: {
            if (urlTextField.text != url)
                urlTextField.text = url
            progressBar.value = loadProgress
        }
        onFullScreenRequested: {
            if (request.toggleOn) {
                headerToolBar.visible = false
                pastVisibility = visibility
                appRoot.showFullScreen();
            }
            else {
                headerToolBar.visible = true
//                appRoot.showNormal();
                appRoot.visibility = pastVisibility
            }
            request.accept();
        }
        onJavaScriptConsoleMessage: {
            footerLogLabel.text = message
        }

        Action {
            shortcut: "Escape"
            onTriggered: {
                if (webEngineView.isFullScreen) {
                    webEngineView.fullScreenCancelled()
                }
            }
        }
    }

    Action {
        shortcut: StandardKey.Quit
        onTriggered: {
            messageDialog.visible = true
        }
    }

    MessageDialog {
        id: messageDialog
        title: "Quit"
        text: "Quit"
        standardButtons: StandardButton.Cancel | StandardButton.Ok
         onAccepted: {
             Qt.quit()
         }
    }

    Timer {
        id: progressBarTimer
        onTriggered: footerRectangle.visible = false;
    }
}
