import LEVEL_PROBE1
import qtgui1
from PyQt5.Qt import *
import sys, time, serial
import threading, os, datetime
from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)
from PyQt5 import QtGui
import cv2
flag = True

if not os.path.exists("LOGS"):
    os.makedirs("LOGS")
file = open("LOGS/" + str(datetime.date.today()).replace("-", "") + ".txt", 'a+')
    # file.write("")

class Worker(QObject):
    finished = pyqtSignal()  # our signal out to the main thread to alert it we've completed our work

    def __init__(self):
        super(Worker, self).__init__()
        self.working = True  # this is our flag to control our loop


    def work(self):
        while self.working:
            print("I'm running")  #Sample logic
            time.sleep(1)
        self.finished.emit()  # alert our gui that the loop stopped


class Worker1(QObject):
    finished1 = pyqtSignal()  # our signal out to the main thread to alert it we've completed our work

    def __init__(self):
        super(Worker1, self).__init__()
        self.working1 = True  # this is our flag to control our loop

    def work(self):
        while self.working1:
            LEVEL_PROBE1.read_data() # Put the logic1 to execute in the first thread


        self.finished1.emit()  # alert our gui that the loop stopped

class Worker2(QObject):
    finished2 = pyqtSignal()  # our signal out to the main thread to alert it we've completed our work

    def __init__(self):
        super(Worker2, self).__init__()
        self.working2 = True  # this is our flag to control our loop

    def work(self):
        while self.working2:
            LEVEL_PROBE1.process_data(int(window1.lineEdit.text()), float(window1.lineEdit_3.text())) # Put the logic2 to execute in the second thread
            print("i am in work"+LEVEL_PROBE1.display_level)
            # window1.lineEdit_2.clear()
            # window1.lineEdit_2.setText(LEVEL_PROBE.display_data)

        self.finished2.emit()  # alert our gui that the loop stopped



class Controller1_qtgui2(QMainWindow, qtgui1.Ui_MainWindow):          #Window 1
    def __init__(self, parent= None):                               #Initialising window1
        super().__init__(parent)
        self.setupUi(self)
        QMainWindow.setWindowFlags(self, Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)# Remove max botton
        self.setWindowIcon(QtGui.QIcon('SMR-LOGO_31aug2013_ico.ico'))

        self.thread = None  # Initialize the thread and the workers
        self.worker = None

        self.thread1 = None
        self.worker1 = None

        self.thread2 = None
        self.worker2 = None
        self.qTimer = QTimer()
        # set interval to 1 s
        self.qTimer.setInterval(2000)  # 1000 ms = 1 s
        # connect timeout signal to signal handler
        self.qTimer.timeout.connect(self.getSensorValue)
        # start timer
        self.qTimer.start()

    def getSensorValue(self):
        # print('%d. call of getSensorValue()' % self.i)
        self.lineEdit_4.setText(LEVEL_PROBE1.display_cal_range+"m")
        self.lineEdit_2.setText(LEVEL_PROBE1.display_current+"mA")
        self.lineEdit_5.setText(LEVEL_PROBE1.display_level + "m")

        # self.pushButton_2.clicked.connect(self.start_loop)

    def closeEvent(self, event):
        try:
            LEVEL_PROBE1.ser_close()
        except:
            pass
    def start_loop(self):

        print("Empty tank value:", int(window1.lineEdit.text()))
        if int(window1.lineEdit.text()) == 20 and float(window1.lineEdit_3.text()) == 0:
            LEVEL_PROBE1.a_max = 7605
            LEVEL_PROBE1.slp = 19.56

        if int(window1.lineEdit.text()) == 2 and float(window1.lineEdit_3.text()) == 0:
            LEVEL_PROBE1.a_max = 5320
            LEVEL_PROBE1.slp = 14.66

        self.port_selection()
        try:
            window1.pushButton_2.setEnabled(False)
            window1.pushButton_3.setEnabled(True)
        except:
            pass

        self.thread = QThread()# a new thread to run our background tasks in
        self.thread1 = QThread()
        self.thread2 = QThread()

        self.worker = Worker()  # a new worker to perform those tasks
        self.worker1 = Worker1()  # a new worker to perform those tasks
        self.worker2 = Worker2()  # a new worker to perform those tasks


        self.worker.moveToThread(self.thread)# move the worker into the thread, do this first before connecting the signals
        self.worker1.moveToThread(self.thread1)# move the worker into the thread, do this first before connecting the signals
        self.worker2.moveToThread(self.thread2)# move the worker into the thread, do this first before connecting the signals

        # self.worker.moveToThread(self.thread1)
        # self.worker.moveToThread(self.thread2)

        self.thread.started.connect(self.worker.work)  # begin our worker object's loop when the thread starts running
        self.thread1.started.connect(self.worker1.work)  # begin our worker object's loop when the thread starts running
        self.thread2.started.connect(self.worker2.work)  # begin our worker object's loop when the thread starts running

        # self.thread1.started.connect(LEVEL_PROBE.read_data)
        # self.thread2.started.connect(LEVEL_PROBE.process_data)
        # # self.pushButton_3.clicked.connect(self.stop_loop)  # stop the loop on the stop button click
        self.worker.finished.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker1.finished1.connect(self.loop_finished)  # do something in the gui when the worker loop ends
        self.worker2.finished2.connect(self.loop_finished)  # do something in the gui when the worker loop ends

        self.worker.finished.connect(self.thread.quit)  # tell the thread it's time to stop running
        self.worker1.finished1.connect(self.thread1.quit)  # tell the thread it's time to stop running
        self.worker2.finished2.connect(self.thread2.quit)  # tell the thread it's time to stop running


        # self.worker.finished.connect(self.thread1.quit)
        # self.worker.finished.connect(self.thread2.quit)


        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
        self.worker1.finished1.connect(self.worker1.deleteLater)  # have worker mark itself for deletion
        self.thread1.finished.connect(self.thread1.deleteLater)  # have thread mark itself for deletion
        self.worker2.finished2.connect(self.worker2.deleteLater)  # have worker mark itself for deletion
        self.thread2.finished.connect(self.thread2.deleteLater)  # have thread mark itself for deletion

        self.thread.finished.connect(self.thread.wait)  # wait for the threads to terminate, otherwise the program crashes before terminating the thread
        self.thread1.finished.connect(self.thread1.wait)  # wait for the threads to terminate, otherwise the program crashes before terminating the thread
        self.thread2.finished.connect(self.thread2.wait)  # wait for the threads to terminate, otherwise the program crashes before terminating the thread





        # self.thread1.finished.connect(self.thread1.deleteLater)
        # self.thread2.finished.connect(self.thread1.deleteLater)
        # # make sure those last two are connected to themselves or you will get random crashes

        self.thread.start()
        self.thread1.start()
        self.thread2.start()

    def stop_loop(self):
        try:
            window1.pushButton_3.setEnabled(False)
            window1.pushButton_2.setEnabled(True)
        except:
            pass

        self.worker.working = False
        self.worker1.working1 = False
        self.worker2.working2 = False
        global flag
        flag = False




        # since thread's share the same memory, we read/write to variables of objects running in other threads
        # so when we are ready to stop the loop, just set the working flag to false

    def loop_finished(self):
        # received a callback from the thread that it completed
        print('Looped Finished')

    def serial_ports(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]


        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def port_selection(self):
        try:
            if LEVEL_PROBE1.ser.is_open:
                LEVEL_PROBE1.ser.close()
        except:
            pass
        LEVEL_PROBE1.ser = serial.Serial(
            port=window1.comboBox.currentText(),
            baudrate=9600,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

    @staticmethod
    def ConvertNumpyToQPixmap(np_img):
        height, width, channel = np_img.shape
        bytesPerLine = 3 * width
        return QPixmap(QImage(np_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())


    def updated(self):
        QMessageBox.about(self, "LEVELPROBE1", "Values updated")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle("fusion")



    # Creating objects for 2 classes
    window1 = Controller1_qtgui2()

    # adding Sameer logo
    currentNumpyImage = cv2.imread('SMR-LOGO_31aug2013_png.png')
    pixmap = window1.ConvertNumpyToQPixmap(currentNumpyImage)
    pixmap = pixmap.scaled(window1.label_3.width(), window1.label_3.height(), transformMode=Qt.SmoothTransformation)
    window1.label_3.setPixmap(pixmap)


    ports= window1.serial_ports() # enumerate available COM ports
    print(ports)
    window1.comboBox.addItems(ports)



    window1.pushButton_2.clicked.connect(window1.start_loop)
    window1.pushButton_3.clicked.connect(window1.stop_loop)  # stop the loop on the stop button click
    print("Display:"+LEVEL_PROBE1.display_level)

    # window1.lineEdit_2.setText(LEVEL_PROBE.display_data)
    window1.pushButton_4.clicked.connect(LEVEL_PROBE1.ser_close)

    window1.show()

    app.exec_()
