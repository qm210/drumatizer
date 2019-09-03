import sys
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt5.QtGui import QColor
from math import pow, sqrt

class EnvelopePoint():

    def __init__(self, time = 0, value = 0, fixedTime = False, fixedValue = False, name = None):
        self.time = time
        self.value = value
        self.fixedTime = fixedTime
        self.fixedValue = fixedValue
        self.name = name

    def __repr__(self):
        return str(self.name) + '(' + ('FIX ' if self.fixedTime else '') + str(self.time) + ', ' + ('FIX ' if self.fixedValue else '') + str(self.value) + ')'

class EnvelopeWidget(QtWidgets.QWidget):

    # clickedPoint = pyqtSignal(int, int) # don't need this quite yet

    def __init__(self, points = None):
        super().__init__()
        self.points = points or []
        self.minTime = 0
        self.minValue = 0
        self.maxTime = 1
        self.maxValue = 1

        # drawing constants
        self.RECT_HMARGIN = 0.05
        self.RECT_VMARGIN = 0.05
        self.AXIS_HMARGIN = 0.20
        self.AXIS_VMARGIN = 0.20
        self.ARROWSIZE = 0.05
        self.POINTSIZE = 0.05
        self.POINTSIZE_PROX = 0.1

        # colors and pens
        self.BGCOLOR = QColor(10, 0, 20)
        self.AXIS_PEN = QtGui.QPen(QColor(180, 255, 255), 3)
        self.POINT_PEN = QtGui.QPen(QColor(180, 255, 255), 1.5)

        self.qrect = QRect()

    def paintEvent(self, event):
        self.qrect = event.rect()
        x = self.qrect.left()
        y = self.qrect.top()
        w = self.qrect.width()
        h = self.qrect.height()

        qp = QtGui.QPainter()
        qp.begin(self)

        qp.fillRect(x + self.RECT_HMARGIN * w, y + self.RECT_VMARGIN * h, (1 - 2 * self.RECT_HMARGIN) * w, (1 - 2 * self.RECT_VMARGIN) * h, self.BGCOLOR)

        qp.setPen(self.AXIS_PEN)
        path = QtGui.QPainterPath()
        path.moveTo(x + self.AXIS_HMARGIN * w - self.ARROWSIZE * h, y + (self.AXIS_VMARGIN + self.ARROWSIZE) * h)
        path.lineTo(x + self.AXIS_HMARGIN * w, y + self.AXIS_VMARGIN * h)
        path.lineTo(x + self.AXIS_HMARGIN * w, y + (1 - self.AXIS_VMARGIN) * h)
        path.lineTo(x + (1 - self.AXIS_HMARGIN) * w, y + (1 - self.AXIS_VMARGIN) * h)
        path.lineTo(x + (1 - self.AXIS_HMARGIN) * w - self.ARROWSIZE * h, y + (1 - self.AXIS_VMARGIN + self.ARROWSIZE) * h)
        qp.drawPath(path)

        if not self.points:
            qp.drawText(event.rect(), Qt.AlignCenter, "no points available..!")
        else:
            path.clear()
            qp.setPen(self.POINT_PEN)
            for ip, p in enumerate(self.points):
                coordX, coordY = self.getCoordinatesOfDimensions(p.time, p.value)
                qp.drawEllipse(coordX - self.POINTSIZE * h/2, coordY - self.POINTSIZE * h/2, self.POINTSIZE * h, self.POINTSIZE * h)
                qp.drawText(x + .8 * self.AXIS_HMARGIN * w, coordY, str(p.value))
                qp.drawText(coordX, y + (1 - .5 * self.AXIS_VMARGIN) * h, str(p.time))

                if ip == 0:
                    path.moveTo(coordX, coordY)
                else:
                    path.lineTo(coordX, coordY)
            qp.drawPath(path)

        qp.end()

    def addPoint(self, time, value, fixedTime = False, fixedValue = False, name = None):
        self.points.append(EnvelopePoint(time, value, fixedTime, fixedValue, name = name))
        print(self.points)

    def setMaxDimensions(self, maxTime, maxValue):
        self.maxTime = maxTime
        self.maxValue = maxValue

    def getCoordinatesOfDimensions(self, time, value):
        coordX = self.qrect.left() + self.qrect.width() * (self.AXIS_HMARGIN + (1 - 2 * self.AXIS_HMARGIN) * (time - self.minTime) / (self.maxTime - self.minTime))
        coordY = self.qrect.bottom() - self.qrect.height() * (self.AXIS_VMARGIN + (1 - 2 * self.AXIS_VMARGIN) * (value - self.minValue) / (self.maxValue - self.minValue))
        return (coordX, coordY)

    def getDimensionsOfCoordinates(self, coordX, coordY):
        pass

    def findPointsNearby(self, coordX, coordY):
        pointsNearby = []
        for p in self.points:
            pX, pY = self.getCoordinatesOfDimensions(p.time, p.value)
            distance = sqrt( pow(pX - coordX, 2) + pow(pY - coordY, 2) )
            if distance < self.POINTSIZE_PROX:
                pointsNearby.append(p)
        return pointsNearby

    def mousePressEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return

        self.mouseMoveEvent(event)
        pointsNearby = self.findPointsNearby(event.pos().x(), event.pos().y())
        if len(pointsNearby) == 1:
            print("the only nearby point is", pointsNearby[0].name)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = EnvelopeWidget()
    window.show()
    sys.exit(app.exec_())