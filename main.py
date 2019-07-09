#################################################################################
#
# Creator: Martin Brisfors, 2019
#
# A GUI tool for executing some of the code we have developed throughout our
# work so far.
#
#################################################################################

import requests
import sys
import PyQt5.QtWidgets as QtWidgets
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtCore import QDateTime, Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import subprocess

#TO_REMOVE
globalIP = '0.0.0.0'

class WidgetGallery(QDialog):
    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        self.selectedString = "selected files:"         #String used to generate list of args for scripts
        self.resize(600,400)                            #Application default resolution

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tabs.blockSignals(True)
        self.createT1()
        self.createT2()
        self.createT3()
        self.tabs.addTab(self.T1,"HTTP GET")
        self.tabs.addTab(self.T2,"Tests")
        self.tabs.addTab(self.T3,"Utils")

        # Currently contains nothing, but it is the tof of the layout above tabs
        topLayout = QHBoxLayout()
        topLayout.addStretch(1)

        # Layout of the main program. Basically just the tabs.
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addWidget(self.tabs)
        mainLayout.addStretch(1)

        # Window layout and header
        self.setLayout(mainLayout)
        self.tabs.blockSignals(False)                   #This is used to prevent an error during startup
        self.setWindowTitle("Deep Learning SCA Tool")

        # Input argument handling
        if len(sys.argv)>2:
            if sys.argv[1] == "-t":
                self.tabs.setCurrentIndex(1)
                temp = self.selectedString
                for i in sys.argv[2:]:
                    temp = temp + "\n" + i
                self.updateSelected(temp)
            elif sys.argv[1] == "-u":
                self.tabs.setCurrentIndex(2)
                temp = self.selectedString
                for i in sys.argv[2:]:
                    temp = temp + "\n" + i
                self.updateSelected(temp)
        elif len(sys.argv)>1:
            self.tabs.setCurrentIndex(1)
            temp = self.selectedString
            for i in sys.argv[1:]:
                temp = temp + "\n" + i
            self.updateSelected(temp)                

#Naming convention atm: T = tab, #X = index starting from 1, L = left side
#So if something is createT1L it means create the left side of tab1...
    def createT1L(self):
        self.tab1 = QWidget()
        tab1Layout = QVBoxLayout(self)
        self.createBL()
        self.createBR()
        tab1Layout.addWidget(self.BL)
        tab1Layout.addWidget(self.BR)
        self.tab1.setLayout(tab1Layout)

#Not sure if there's a better way to do this since I want elements to be aligned.
#The block separation in this code represents GUI modules.
#Naming convention: t = tab, #X = index starting from 1, l = left side
#Naming convention: b = button, s = script, h = help
#Each widget has its own layout variable where if possible it has the same prefix
    def createT2L(self):
        self.tab2 = QWidget()
        t2lLayout = QVBoxLayout(self)

        t2b1Widget = QWidget()
        t2b1Layout = QHBoxLayout()
        tab2Button1 = QPushButton("Files")
        tab2Button1h = QPushButton("?")
        t2b1Layout.addWidget(tab2Button1, 40)
        t2b1Layout.addWidget(tab2Button1h, 1)
        t2b1Widget.setLayout(t2b1Layout)
        t2lLayout.addWidget(t2b1Widget)

        self.tab2TextWidget = QWidget()
        tab2TextLayout = QHBoxLayout()
        self.tab2.textEdit = QTextEdit()
        self.tab2.textEdit.setPlainText(self.selectedString)
        tab2Texth = QPushButton("?")
        tab2TextLayout.addWidget(self.tab2.textEdit, 40)
        tab2TextLayout.addWidget(tab2Texth, 1)
        self.tab2TextWidget.setLayout(tab2TextLayout)
        t2lLayout.addWidget(self.tab2TextWidget)

        t2dropdownWidget = QWidget()
        t2dropdownLayout = QHBoxLayout()
        t2dropdown = QComboBox()
        t2dropdown.addItem("option 1 tbd")
        t2dropdown.addItem("option 2 tbd")
        t2dropdown.addItem("option 3 tbd")
        t2dropdownh = QPushButton("?")
        t2dropdownLayout.addWidget(t2dropdown, 40)
        t2dropdownLayout.addWidget(t2dropdownh, 1)
        t2dropdownWidget.setLayout(t2dropdownLayout)
        t2lLayout.addWidget(t2dropdownWidget)

#SELECTION GROUP 1
        t2Group1 = QWidget()
        t2ConfirmLayout = QHBoxLayout()
        tab2Confirm = QPushButton("Confirm")
        tab2Confirmh = QPushButton("?")
        t2ConfirmLayout.addWidget(tab2Confirm, 40)
        t2ConfirmLayout.addWidget(tab2Confirmh, 1)
        t2Group1.setLayout(t2ConfirmLayout)
        t2lLayout.addWidget(t2Group1)

#SELECTION GROUP 2
        t2Group2 = QWidget()
        t2s1Layout = QHBoxLayout()
        tab2Script1 = QPushButton("average rank test")
        tab2Script1h = QPushButton("?")
        t2s1Layout.addWidget(tab2Script1, 40)
        t2s1Layout.addWidget(tab2Script1h, 1)
        t2Group2.setLayout(t2s1Layout)
        t2Group2.hide()
        t2lLayout.addWidget(t2Group2)
        self.tab2.setLayout(t2lLayout)

#SELECTION GROUP 3
        t2Group3 = QWidget()
        t2HideLayout = QHBoxLayout()
        tab2Hide = QPushButton("Hide")
        tab2Hideh = QPushButton("?")
        t2HideLayout.addWidget(tab2Hide, 40)
        t2HideLayout.addWidget(tab2Hideh, 1)
        t2Group3.setLayout(t2HideLayout)
        t2Group3.hide()
        t2lLayout.addWidget(t2Group3)

#A lot of local functions will be used as well as some "global" (bound to super) functions. 
#The following is a list of functions that will be used on buttons presses or text changes
#Naming convention: info = update right hand side info column.
        def filebrowserinfo():
                info = "Browse for files to add to the list in the text editor. Trained models are of type .h5 while history files and raw results data are .npy."
                self.updateInfo(info,self.tabs.currentIndex())

        def selectedinfo():
                info = "This is an editable list of files currently selected. You can edit it by just deleting text. Never remove the first line and never enter non-file non-empty strings on a line."
                self.updateInfo(info,self.tabs.currentIndex())

        def dropdowninfo():
                info = "Use the dropdown menu to select which script to run on the selected files. It is up to you as the user to not make a mistake..."
                self.updateInfo(info,self.tabs.currentIndex())

        def script1info():
                info = "Average rank test for selected models. More info to come."
                self.updateInfo(info,self.tabs.currentIndex())

        def confirminfo():
                info = "Placeholder."
                self.updateInfo(info,self.tabs.currentIndex())

        def textchanget2():
                 temp = self.tab2.textEdit.toPlainText()
                 self.updateSelected(temp, ignore = 1  , current = self.tabs.currentIndex())

        def clickedt2b1():
                 self.openFileNamesDialog()

        def clickedConfirm():
                 print(self.selectedString)

        def avgrank():
                args = self.splitter(self.selectedString)
                subprocess.call(['python', 'scripts/average_rank_test.py'] + args[1:])

        def selection(i):
            if i == 0:
                t2Group1.show()
                t2Group2.hide()
                t2Group3.hide()

            if i == 1:
                t2Group1.hide()
                t2Group2.show()
                t2Group3.hide()

            if i == 2:
                t2Group1.hide()
                t2Group2.hide()
                t2Group3.show()

#Actually bind the scripts to the buttons and textedits. This needs to be defined after the
#functions they will be used which is why they are hidden down here
        tab2Button1.clicked.connect(clickedt2b1)
        tab2Button1h.clicked.connect(filebrowserinfo)
        tab2Texth.clicked.connect(selectedinfo)
        t2dropdownh.clicked.connect(dropdowninfo)
        tab2Confirm.clicked.connect(clickedConfirm)
        tab2Confirmh.clicked.connect(confirminfo)
        tab2Script1.clicked.connect(avgrank)
        tab2Script1h.clicked.connect(script1info)
        self.tab2.textEdit.textChanged.connect(textchanget2)
        t2dropdown.currentIndexChanged.connect(selection)


    def createT3L(self):
        self.tab3 = QWidget()
        t3lLayout = QVBoxLayout(self)

        t3b1Widget = QWidget()
        t3b1Layout = QHBoxLayout()
        tab3Button1 = QPushButton("Files")
        tab3Button1h = QPushButton("?")
        t3b1Layout.addWidget(tab3Button1, 40)
        t3b1Layout.addWidget(tab3Button1h, 1)
        t3b1Widget.setLayout(t3b1Layout)
        t3lLayout.addWidget(t3b1Widget)

        self.tab3TextWidget = QWidget()
        tab3TextLayout = QHBoxLayout()
        self.tab3.textEdit = QTextEdit()
        self.tab3.textEdit.setPlainText(self.selectedString)
        tab3Texth = QPushButton("?")
        tab3TextLayout.addWidget(self.tab3.textEdit, 40)
        tab3TextLayout.addWidget(tab3Texth, 1)
        self.tab3TextWidget.setLayout(tab3TextLayout)
        t3lLayout.addWidget(self.tab3TextWidget)

        t3dropdownWidget = QWidget()
        t3dropdownLayout = QHBoxLayout()
        t3dropdown = QComboBox()
        t3dropdown.addItem("option 1 tbd")
        t3dropdown.addItem("option 2 tbd")
        t3dropdown.addItem("option 3 tbd")
        t3dropdownh = QPushButton("?")
        t3dropdownLayout.addWidget(t3dropdown, 40)
        t3dropdownLayout.addWidget(t3dropdownh, 1)
        t3dropdownWidget.setLayout(t3dropdownLayout)
        t3lLayout.addWidget(t3dropdownWidget)

#SELECTION GROUP 1
        t3Group1 = QWidget()
        t3ConfirmLayout = QHBoxLayout()
        tab3Confirm = QPushButton("Confirm")
        tab3Confirmh = QPushButton("?")
        t3ConfirmLayout.addWidget(tab3Confirm, 40)
        t3ConfirmLayout.addWidget(tab3Confirmh, 1)
        t3Group1.setLayout(t3ConfirmLayout)
        t3lLayout.addWidget(t3Group1)

#SELECTION GROUP 2
        t3Group2 = QWidget()
        t3s1Layout = QHBoxLayout()
        tab3Script1 = QPushButton("Printer.py")
        tab3Script1h = QPushButton("?")
        t3s1Layout.addWidget(tab3Script1, 40)
        t3s1Layout.addWidget(tab3Script1h, 1)
        t3Group2.setLayout(t3s1Layout)
        t3Group2.hide()
        t3lLayout.addWidget(t3Group2)

#SELECTION GROUP 3
        t3Group3 = QWidget()
        t3HideLayout = QHBoxLayout()
        tab3Hide = QPushButton("Hide widgets")
        tab3Hideh = QPushButton("?")
        t3HideLayout.addWidget(tab3Hide, 40)
        t3HideLayout.addWidget(tab3Hideh, 1)
        t3Group3.setLayout(t3HideLayout)
        t3Group3.hide()
        t3lLayout.addWidget(t3Group3)

        self.tab3.setLayout(t3lLayout)

        def textchanget3():
                 temp = self.tab3.textEdit.toPlainText()
                 self.updateSelected(temp, ignore = 2, current = self.tabs.currentIndex())

        def clickedt3b1():
                 self.openFileNamesDialog()

        def filebrowserinfo():
                info = "Browse for files to add to the list in the text editor. Trained models are of type .h5 while history files and raw results data are .npy."
                self.updateInfo(info,self.tabs.currentIndex())

        def selectedinfo():
                info = "This is an editable list of files currently selected. You can edit it by just deleting text. Never remove the first line and never enter non-file non-empty strings on a line."
                self.updateInfo(info,self.tabs.currentIndex())

        def dropdowninfo():
                info = "Use the dropdown menu to select which script to run on the selected files. It is up to you as the user to not make a mistake..."
                self.updateInfo(info,self.tabs.currentIndex())

        def script1info():
                info = "Placeholder for a util script. Currently just prints arguments being sent."
                self.updateInfo(info,self.tabs.currentIndex())

        def clickedConfirm():
                 print(self.selectedString)

        def script1():
                 args = self.splitter(self.selectedString)
                 subprocess.call(['python', 'scripts/printer.py'] + args[1:])

        def selection(i):
            if i == 0:
                t3Group1.show()
                t3Group2.hide()
                t3Group3.hide()

            if i == 1:
                t3Group1.hide()
                t3Group2.show()
                t3Group3.hide()

            if i == 2:
                t3Group1.hide()
                t3Group2.hide()
                t3Group3.show()

        tab3Button1.clicked.connect(clickedt3b1)  
        tab3Button1h.clicked.connect(filebrowserinfo)
        t3dropdownh.clicked.connect(dropdowninfo)  
        tab3Confirm.clicked.connect(clickedConfirm)
        tab3Script1.clicked.connect(script1)
        tab3Script1h.clicked.connect(script1info)
        tab3Texth.clicked.connect(selectedinfo)
        self.tab3.textEdit.textChanged.connect(textchanget3)
        t3dropdown.currentIndexChanged.connect(selection)


#The following three definitions are for right hand side of tabs, used for displaying info.
    def createT1R(self):
        self.T1R = QWidget()
        t1rLayout = QVBoxLayout(self)
        self.tab1info = QLabel()
        self.tab1info.setWordWrap(True)
        self.tab1info.setText("press the ? buttons to get more info")
        t1rLayout.addWidget(self.tab1info)
        self.T1R.setLayout(t1rLayout)

    def createT2R(self):
        self.T2R = QWidget()
        t2rLayout = QVBoxLayout(self)
        self.tab2info = QLabel()
        self.tab2info.setWordWrap(True)
        self.tab2info.setText("press the ? buttons to get more info")
        t2rLayout.addWidget(self.tab2info)
        self.T2R.setLayout(t2rLayout)

    def createT3R(self):
        self.T3R = QWidget()
        t3rLayout = QVBoxLayout(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        self.T3R.setSizePolicy(sizePolicy)
        self.tab3info = QLabel()
        self.tab3info.setWordWrap(True)
        self.tab3info.setText("press the ? buttons to get more info")
        t3rLayout.addWidget(self.tab3info)
        self.T3R.setLayout(t3rLayout)

#The actual tabs. Naming convention will have to be changed to be consistent later.
#These are basically just containers holding the two halves of each tab.
    def createT1(self):
        self.T1 = QGroupBox()
        t1Layout = QHBoxLayout()
        self.createT1L()
        self.createT1R()
        t1Layout.addWidget(self.tab1)
        t1Layout.addWidget(self.T1R)
        self.T1.setLayout(t1Layout)        

    def createT2(self):
        self.T2 = QGroupBox()
        t2Layout = QHBoxLayout()
        self.createT2L()
        self.createT2R()
        self.T2R.setMaximumWidth(100)
        t2Layout.addWidget(self.tab2)   
        t2Layout.addWidget(self.T2R)
        self.T2.setLayout(t2Layout)

    def createT3(self):
        self.T3 = QGroupBox()
        t3Layout = QHBoxLayout()
        self.createT3L()
        self.createT3R()
        self.T3R.setMaximumWidth(100)
        t3Layout.addWidget(self.tab3)
        t3Layout.addWidget(self.T3R)
        self.T3.setLayout(t3Layout)

#This will be changed later. The first draft of this program used quadrants for its design.
#This was the old Bottom Right quadrant. Will be changed to use same design as t2 and t3.
    def createBL(self):
        self.BL = QGroupBox("Results")
        self.BL.textEdit = QTextEdit()
        self.BL.textEdit.setPlainText("waiting for results...")
        mylayout = QGridLayout()
        mylayout.addWidget(self.BL.textEdit,0,0,1,2)
        mylayout.setRowStretch(5,1)
        self.BL.setLayout(mylayout)

    def createBR(self):
        self.BR = QGroupBox("IP address/URL")
        self.BR.lineEdit = QLineEdit('0.0.0.0')
        confirmIPButton = QPushButton("Confirm")

        def on_button_clicked():
                globalIP = self.BR.lineEdit.text()
                r = requests.get(globalIP)
                self.BL.textEdit.setPlainText('HEADER:\n\n' + str(r.headers) + '\n\nCONTENT:\n\n' + str(r.content))
                alert = QMessageBox()
                alert.setText(str(r.status_code))
                alert.exec_()

        confirmIPButton.clicked.connect(on_button_clicked)

        layout = QGridLayout()
        layout.addWidget(self.BR.lineEdit, 0, 0, 1, 2)
        layout.addWidget(confirmIPButton,1,0,1,2)
        layout.setRowStretch(5, 1)
        self.BR.setLayout(layout)

#File browser used to load files if you didn't use the terminal for that.
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Model Files (*.h5);;Numpy Arrays (*.npy)", options=options)
        if files:
            temp = self.selectedString
            for i in files:
              temp = temp + "\n" + i
            self.updateSelected(temp)

#Updates and synchronizes the loaded file lists on t2 and t3. 
#The conditionals prevent infinite recursion.
    def updateSelected(self, newSelected, ignore = 0, current = 0):
        self.selectedString = newSelected
        if ignore is not 1:
            if current is not 1: self.tab2.textEdit.setPlainText(self.selectedString)
        if ignore is not 2:
            if current is not 2: self.tab3.textEdit.setPlainText(self.selectedString)

#Update the right hand side info bar with whatever query the user clicked.
    def updateInfo(self, info, tabnumber):
        if tabnumber == 0:
            self.tab1info.setText(info)

        if tabnumber == 1:
            self.tab2info.setText(info)

        if tabnumber == 2:
            self.tab3info.setText(info)

#I don't think this is used anymore? Probably old debugging thing.
#Will be removed if it turns out it is useless.
    def tabSwitch(self):
        print(str(self.tabs.currentIndex()))
        if self.tabs.currentIndex() is not 0:
            if self.tabs.currentIndex() == 1:
                temp = self.tab2.textEdit.toPlainText()
                self.updateSelected(temp)
            if self.tabs.currentIndex() == 2:
                temp = self.tab3.textEdit.toPlainText()
                self.updateSelected(temp)
        self.updateSelected(self.selectedString)

#Script for splitting the string stored in the text edit into a list strings
#to send as args for the linked scripts
    def splitter(self, s):
        return [line.strip() for line in s.splitlines() if line.strip()]

if __name__ == '__main__':
#    appctxt = ApplicationContext()
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    gallery.show()
    sys.exit(app.exec_())

