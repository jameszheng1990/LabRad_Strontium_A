from camera.clients.default import CameraClient

class TOFtcamClient(CameraClient):
    name = 'TOFtcam' # Name MUST be the same as device_name


if __name__ == '__main__':
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication([])
    import client_tools.qt5reactor as qt5reactor
    qt5reactor.install()
    from twisted.internet import reactor
    widget = TOFtcamClient(reactor)
    widget.show()
    reactor.run()