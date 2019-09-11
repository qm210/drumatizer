import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt5.QtGui import QColor
from math import pow, sqrt, log, exp

#from EnvelopeModel import *
from DoubleInputDialog import DoubleInputDialog
import mayStyle


class EnvelopeWidget(QtWidgets.QWidget):

    pointsChanged = pyqtSignal()

    def __init__(self, parent, points = None):
        super().__init__()
        self.parent = parent
        self.qrect = QRect()

        self.points = points or []
        self.minTime = 0
        self.minValue = 0
        self.maxTime = 1
        self.maxValue = 1
        self.logValue = False

        self.draggingPoint = None
        self.draggingPointOriginalTime = None
        self.draggingPointOriginalValue = None

        # drawing constants
        self.RECT_HMARGIN = 0.0
        self.RECT_VMARGIN = 0.0
        self.AXIS_LMARGIN = 0.07
        self.AXIS_RMARGIN = 0.02
        self.AXIS_TMARGIN = 0.033
        self.AXIS_BMARGIN = 0.15
        self.POINTSIZE = 0.05
        self.POINTSIZE_PROX = 0.03
        self.LABEL_LMARGIN = 0.06
        self.LABEL_BMARGIN = 0.03
        # colors, pens, fonts
        self.BGCOLOR = QColor(*mayStyle.group_bgcolor)
        self.TEXTCOLOR = QColor(*mayStyle.default_textcolor)
        self.AXIS_PEN = QtGui.QPen(self.TEXTCOLOR, 3)
        self.POINT_PEN = QtGui.QPen(self.TEXTCOLOR, 1.5)
        self.TEXT_FONT = QtGui.QFont("Roboto", 12)
        self.LABEL_FONT = QtGui.QFont("Roboto Condensed", 9)


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
        path.moveTo(x + self.AXIS_LMARGIN * w, y + self.AXIS_TMARGIN * h)
        path.lineTo(x + self.AXIS_LMARGIN * w, y + (1 - self.AXIS_BMARGIN) * h)
        path.lineTo(x + (1 - self.AXIS_RMARGIN) * w, y + (1 - self.AXIS_BMARGIN) * h)
        qp.drawPath(path)

        if not self.points:
            qp.setFont(self.TEXT_FONT)
            qp.drawText(event.rect(), Qt.AlignCenter, "no points available..!")
        else:
            path.clear()
            qp.setPen(self.POINT_PEN)
            qp.setFont(self.LABEL_FONT)
            for ip, p in enumerate(self.points):
                coordX, coordY = self.getCoordinatesOfDimensions(p.time, p.value)
                qp.drawEllipse(coordX - self.POINTSIZE * h/2, coordY - self.POINTSIZE * h/2, self.POINTSIZE * h, self.POINTSIZE * h)
                if not (p.fixedTime and p.fixedValue):
                    axisX = x + self.LABEL_LMARGIN * w
                    self.drawText(qp, axisX, coordY, Qt.AlignRight | Qt.AlignVCenter, str(p.value))
                    axisY = y + (1 - self.LABEL_BMARGIN) * h
                    self.drawText(qp, coordX, axisY, Qt.AlignHCenter, str(p.time))

                if ip == 0:
                    path.moveTo(coordX, coordY)
                else:
                    path.lineTo(coordX, coordY)

            path.lineTo(x + w, coordY)
            qp.drawPath(path)

        qp.end()


    def drawText(self, qp, x, y, flags, text):
        size = 32767
        y -= size
        if flags & Qt.AlignHCenter:
            x -= 0.5*size
        elif flags & Qt.AlignRight:
            x -= size
        if flags & Qt.AlignVCenter:
            y += 0.5*size
        elif flags & Qt.AlignTop:
            y += size
        else:
            flags |= Qt.AlignBottom
        rect = QtCore.QRectF(x, y, size, size)
        qp.drawText(rect, flags, text)


    def loadEnvelope(self, envelope):
        self.points = envelope.points if envelope else []
        self.update()


    def setDimensions(self, maxTime = None, maxValue = None, minTime = None, minValue = None, logValue = None):
        if maxTime:
            self.maxTime = maxTime
        if minTime:
            self.minTime = minTime
        if maxValue:
            self.maxValue = maxValue
        if minValue:
            self.minValue = minValue
        if logValue:
            self.logValue = logValue
            if self.logValue and self.minValue == 0:
                print("EnvelopeWidget can't have logarithmic axis when minimum is zero..!")
                self.logValue = False
        self.update()


    def getCoordinatesOfDimensions(self, time, value):
        anti_HMargin = 1 - self.AXIS_LMARGIN - self.AXIS_RMARGIN
        anti_VMargin = 1 - self.AXIS_TMARGIN - self.AXIS_BMARGIN

        coordX = self.qrect.left() + self.qrect.width() * (self.AXIS_LMARGIN + anti_HMargin * (time - self.minTime) / (self.maxTime - self.minTime))

        if self.logValue:
            coordY = self.qrect.bottom() - self.qrect.height() * (self.AXIS_BMARGIN + anti_VMargin * (log(value) - log(self.minValue)) / (log(self.maxValue) - log(self.minValue)))
        else:
            coordY = self.qrect.bottom() - self.qrect.height() * (self.AXIS_BMARGIN + anti_VMargin * (value - self.minValue) / (self.maxValue - self.minValue))

        return (coordX, coordY)


    def getDimensionsOfCoordinates(self, coordX, coordY):
        anti_HMargin = 1 - self.AXIS_LMARGIN - self.AXIS_RMARGIN
        anti_VMargin = 1 - self.AXIS_TMARGIN - self.AXIS_BMARGIN

        timeFactor = self.qrect.width() * anti_HMargin / (self.maxTime - self.minTime)
        timeOffset = self.qrect.left() + self.qrect.width() * self.AXIS_LMARGIN
        time = self.minTime + (coordX - timeOffset) / timeFactor

        if self.logValue:
            valueFactor = -self.qrect.height() * anti_VMargin / (log(self.maxValue) - log(self.minValue))
            valueOffset = self.qrect.bottom() - self.qrect.height() * self.AXIS_BMARGIN
            value = self.minValue * exp( (coordY - valueOffset) / valueFactor )
        else:
            valueFactor = -self.qrect.height() * anti_VMargin / (self.maxValue - self.minValue)
            valueOffset = self.qrect.bottom() - self.qrect.height() * self.AXIS_BMARGIN
            value = self.minValue + (coordY - valueOffset) / valueFactor
            # TODO: something weird happens in this case with rounding the value to minValue, close to zero... wtf??
        return round(max(time, self.minTime), 2), round(value if value > self.minValue else self.minValue, 2)


    def findNextNeighbor(self, coordX, coordY):
        nextNeighbor = None
        minDistance = None
        for p in self.points:
            pX, pY = self.getCoordinatesOfDimensions(p.time, p.value)
            distance = sqrt( pow(pX - coordX, 2) + pow(pY - coordY, 2) )
            if distance < self.POINTSIZE_PROX * self.qrect.width():
                if nextNeighbor is None or distance < minDistance:
                    nextNeighbor = p
                    minDistance = distance
        return nextNeighbor


    def mousePressEvent(self, event):
        nextNeighbor = self.findNextNeighbor(event.pos().x(), event.pos().y())
        if nextNeighbor is None:
            return
        self.draggingPoint = nextNeighbor
        self.draggingPointOriginalTime = self.draggingPoint.time
        self.draggingPointOriginalValue = self.draggingPoint.value

        if event.button() == Qt.RightButton:
            inputDialog = DoubleInputDialog(self, maxValue = self.maxValue, point = self.draggingPoint)
            if inputDialog.exec_():
                time = round(inputDialog.timeBox.value(), inputDialog.precision)
                value = round(inputDialog.valueBox.value(), inputDialog.precision)
                self.draggingPoint.dragTo(time, value)
                self.finishPointChange()


    def mouseMoveEvent(self, event):
        if self.draggingPoint:
            newTime, newValue = self.getDimensionsOfCoordinates(event.pos().x(), event.pos().y())
            self.draggingPoint.dragTo(newTime, newValue)
            self.repaint()


    def mouseReleaseEvent(self, event):
        self.finishPointChange()
        self.draggingPoint = None
        self.update()


    def finishPointChange(self):
        if self.draggingPoint:
            if any(point.time >= nextPoint.time for point, nextPoint in zip(self.points, self.points[1:])) \
                or self.isOutsideOfWidget(*self.draggingPoint.values()):
                    self.draggingPoint.dragTo(self.draggingPointOriginalTime, self.draggingPointOriginalValue)
            else:
                self.pointsChanged.emit()


    def isOutsideOfWidget(self, time, value):
        coordX, coordY = self.getCoordinatesOfDimensions(time, value)
        return coordX < self.qrect.left() or coordX > self.qrect.right() or coordY < self.qrect.top() or coordY > self.qrect.bottom()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = EnvelopeWidget()
    window.show()
    sys.exit(app.exec_())