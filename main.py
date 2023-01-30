# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide2.QtCore import Qt, QUrl, QFile, QJsonDocument
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWebEngine import QtWebEngine
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()
        self.filters = Filters()

    def interceptRequest(self, info):
        strUrl = info.requestUrl().toString()
        info.block(self.filters.chekUrl(strUrl))


class Filters:
    def __init__(self):
        self.blacklist = {}
        jsonFile = QFile("easylist.json")
        if not jsonFile.open(QFile.ReadOnly):
            return
        byteArray = jsonFile.readAll()
        jsonDocument = QJsonDocument.fromJson(byteArray)
        root = jsonDocument.object()
        self.blacklist = root["blacklist"]

    def chekUrl(self, url):
        if len(self.blacklist) > 0:
            for key in self.blacklist.keys():
                requestUrlList = self.blacklist[key]
                for item in requestUrlList:
                    if url.find(item) > -1:
                        return True
        return False


if __name__ == "__main__":
    appName = "PyQMLWebBr"

    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    QGuiApplication.setOrganizationName("Raven-98")
    QGuiApplication.setApplicationName(appName)
    QtWebEngine.initialize()
    app = QGuiApplication(sys.argv)

    requestInterceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile().defaultProfile().setRequestInterceptor(requestInterceptor)

    engine = QQmlApplicationEngine()
    engine.addImportPath(str(Path(__file__).parent))
    engine.rootContext().setContextProperty("appName", appName)
    engine.quit.connect(app.quit)
    engine.load(QUrl.fromLocalFile('main.qml'))
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
