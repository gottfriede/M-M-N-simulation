import queue
import numpy
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from functools import partial

import mmnUi

class Event :
    def __init__(self, newCustomerId, newWindowId, newEventType, newOccurTime) :
        self.customerId = newCustomerId
        self.windowId = newWindowId
        self.eventType = newEventType
        self.occurTime = newOccurTime

    def __lt__(self, other) :
        if (self.occurTime == other.occurTime) :
            return self.customerId < other.customerId
        else :
            return self.occurTime < other.occurTime
    
    def getCustomerId(self) :
        return self.customerId
    
    def getWindowId(self) :
        return self.windowId

    def getEventType(self) :
        return self.eventType

    def getOccurTime(self) :
        return self.occurTime

    def output(self) :
        sentence = ""
        sentence = sentence + "Time: " + str(round(self.occurTime, 2)) + ", "
        if (self.eventType == 1) :
            sentence = sentence + str(self.customerId) + " arrived"
        if (self.eventType == 2) :
            sentence = sentence + str(self.customerId) + " began to be served at window " + str(self.windowId)
        if (self.eventType == 3) :
            sentence = sentence + str(self.customerId) + " left window " + str(self.windowId)
        ui.textBrowser.append(sentence)

averageArriveTime = 0
averageServeTime = 0
customerNumber = 0
queueMaxLength = 0
windowNumber = 0

eventList = queue.PriorityQueue()
waitingQueue = queue.Queue(queueMaxLength)
windows = []
arriveTimeList = []
leaveTimeList = []
serveBeginTimeList = []
serveTimeList = []
lastTime = 0
totalTime = 0
queueArea = 0

def init() :
    for i in range(windowNumber) :
        windows.append(0)
        serveBeginTimeList.append(0)
        serveTimeList.append(0)
    produceCustomers(averageArriveTime, customerNumber)

def produceCustomers(averageArriveTime, number) :
    tmpTime = 0
    tmpCustomerId = 0
    for i in range(customerNumber) :
        arriveInterval = numpy.random.exponential(averageArriveTime)
        tmpTime = tmpTime + arriveInterval
        tmpCustomerId = tmpCustomerId + 1
        eventList.put(Event(tmpCustomerId, -1, 1, tmpTime))
        arriveTimeList.append(tmpTime)

def serveTime() :
    normal = 0
    while (normal <= 0) :
        normal = numpy.random.normal() + averageServeTime
    return normal

def getWaitingWindow() :
    for i in range(len(windows)) :
        if (windows[i] == 0) :
            return i
    return -1

def simulate() :
    global lastTime, totalTime, queueArea
    while (not eventList.empty()) :
        flush()
        nextEvent = eventList.get()
        lastTime = totalTime
        totalTime = nextEvent.getOccurTime()
        queueArea = queueArea + waitingQueue.qsize() * (totalTime - lastTime)
        nextEvent.output()
        if (nextEvent.getEventType() == 1) :
            tmpCustomerId = nextEvent.getCustomerId()
            tmpTime = nextEvent.getOccurTime()
            window = getWaitingWindow()
            if (window == -1) :
                if (waitingQueue.qsize() >= queueMaxLength) :
                    ui.textBrowser.append("Warning: The queue has reached the maximum number of people.\nThe simulation has stopped")
                    return
                waitingQueue.put(tmpCustomerId)
            else :
                eventList.put(Event(tmpCustomerId, window, 2, tmpTime))
        elif (nextEvent.getEventType() == 2) :
            tmpCustomerId = nextEvent.getCustomerId()
            tmpTime = nextEvent.getOccurTime()
            tmpWindow = nextEvent.getWindowId()
            windows[tmpWindow] = 1
            serveBeginTimeList[tmpWindow] = tmpTime
            eventList.put(Event(tmpCustomerId, tmpWindow, 3, tmpTime+serveTime()))
        elif (nextEvent.getEventType() == 3) :
            tmpWindow = nextEvent.getWindowId()
            tmpTime = nextEvent.getOccurTime()
            leaveTimeList.append(nextEvent.getOccurTime())
            serveTimeList[tmpWindow] = serveTimeList[tmpWindow] + tmpTime - serveBeginTimeList[tmpWindow]
            if (waitingQueue.empty()) :
                windows[tmpWindow] = 0
            else :
                tmpCustomerId = waitingQueue.get()
                eventList.put(Event(tmpCustomerId, tmpWindow, 2, tmpTime))
    ui.textBrowser.append("Successfully done the simulation")

def flush() :
    ui.lcdNumber.display(round(totalTime, 2))
    ui.progressBar.setValue(waitingQueue.qsize())
    QApplication.processEvents()
    
def output() :
    ans = 0
    if (len(leaveTimeList) != 0) :
        for i in range(len(leaveTimeList)) :
            ans += leaveTimeList[i] - arriveTimeList[i]
        ans = ans / len(leaveTimeList)
    ui.lineEdit_5.setText(str(round(ans, 2)))
    ans = []
    for i in range(len(windows)) :
        ui.textBrowser_2.append("第 " + str(i) + " 号窗口： " + str(round(serveTimeList[i] / totalTime * 100, 2)) + "%\n")
    ans = queueArea / totalTime
    ui.lineEdit_6.setText(str(round(ans, 2)))

def convert(ui) :
    global averageArriveTime, averageServeTime, customerNumber, queueMaxLength, windowNumber
    averageArriveTime = int(ui.lineEdit_3.text())
    averageServeTime = int(ui.lineEdit_4.text())
    customerNumber = int(ui.lineEdit_2.text())
    queueMaxLength = int(ui.lineEdit.text())
    windowNumber = int(ui.spinBox.text())
    ui.progressBar.setMaximum(queueMaxLength)
    init()
    simulate()
    output()

def reset(ui) :
    global queueArea
    ui.lineEdit_5.setText("")
    ui.lineEdit_6.setText("")
    ui.textBrowser_2.setText("")
    ui.textBrowser.setText("")
    ui.lcdNumber.display(0)
    windows.clear()
    arriveTimeList.clear()
    leaveTimeList.clear()
    serveBeginTimeList.clear()
    serveTimeList.clear()
    lastTime = 0
    totalTime = 0
    queueArea = 0

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = mmnUi.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.pushButton.clicked.connect(partial(convert, ui))
    ui.pushButton_3.clicked.connect(partial(reset, ui))
    sys.exit(app.exec_())
