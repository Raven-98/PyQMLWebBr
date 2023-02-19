# This Python file uses the following encoding: utf-8
import sys
from pathlib import Path

from PySide2.QtCore import Qt, QUrl
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWebEngine import QtWebEngine
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile

from adblockparser import AdblockRules

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self):
        super().__init__()

        with open("easylist.txt") as f:
            raw_rules = f.readlines()
            self.rules = AdblockRules(raw_rules)

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        if self.rules.should_block(url):
            info.block(True)


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
