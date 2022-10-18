from datetime import datetime
import locale
import shutil
from tkinter import BOTH, messagebox
import tkinter as tk
from tkinter import *
from os import listdir, startfile
from pathlib import Path
from os.path import isfile, isdir, join, getmtime, getsize
import subprocess, os, platform
from tkinter.ttk import Treeview
from PyQt5.QtWidgets import QApplication, QAbstractItemView, QLineEdit, QSplitter, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QToolButton, QMenu, QWidget, QAction,QMessageBox, QDirModel, QFileSystemModel, QTreeView, QListView, QGridLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt,QDir, QVariant
import sys

    
class App(QMainWindow):

    def __init__(self, initialDir):
        super().__init__()
        
        # Variables
        self.currentDir = initialDir
        self.showFileExtensions = 1

        # App init
        self.initUI()

    def initUI(self):
        # Top menu
        self.createTopMenu()
        self.toolbar = self.addToolBar("actionToolBar")
        self.toolbar.setMovable(False)

        # Status bar
        self.statusBar()
        self.createActionBar()

        dirModel = QFileSystemModel()
        dirModel.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        dirModel.setRootPath(QDir.rootPath())

        self.sideExplorer = QTreeView()
        self.sideExplorer.setModel(dirModel)
        self.sideExplorer.hideColumn(3)
        self.sideExplorer.hideColumn(2)
        self.sideExplorer.hideColumn(1)
        self.sideExplorer.header().hide()
        self.sideExplorer.clicked.connect(self.navigate)
        self.sideExplorer.uniformRowHeights = True

        self.mainModel = QFileSystemModel()
        self.mainModel.setRootPath(QDir.rootPath())
        self.mainModel.setReadOnly(False)
        
        self.mainExplorer = QListView()
        self.mainExplorer.setModel(self.mainModel)
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(QDir.homePath()))
        self.mainExplorer.doubleClicked.connect(self.navigate)
        self.mainExplorer.uniformItemSizes = True
        layout = QVBoxLayout()
        explorerLayout = QHBoxLayout()

        layout.addLayout(explorerLayout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.sideExplorer)
        splitter.addWidget(self.mainExplorer)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([200, 300])
        explorerLayout.addWidget(splitter)

        # Main widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextItemMenu) 

        self.setLayout(layout)
        self.setGeometry(800,600,600,560)
        self.navigate(self.mainModel.setRootPath(QDir.homePath()))
        self.show()

    def donothing():
        x = 0

    def about(self):
        window = Toplevel(self)
        window.title("About pyTExplorer");
        window.resizable(width=False, height=False);
        window.geometry('250x400')
        newlabel = Label(window, text = "Made by Antonin Desfontaines")
        newlabel.pack()
    def createActionBar(self):
        self._navigateBackButton = QToolButton()                                     
        self._navigateBackButton.setCheckable(True)                                  
        self._navigateBackButton.setChecked(False)                                   
        self._navigateBackButton.setArrowType(Qt.LeftArrow)
        self._navigateBackButton.setAutoRaise(True)
        #self._navigateBackButton.setIcon(QIcon("test.jpg"))
        self._navigateBackButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self._navigateBackButton.clicked.connect(self.showDetail)

        self._navigateForwardButton = QToolButton()                                     
        self._navigateForwardButton.setCheckable(True)                                  
        self._navigateForwardButton.setChecked(False)                                   
        self._navigateForwardButton.setArrowType(Qt.RightArrow)
        self._navigateForwardButton.setAutoRaise(True)
        #self._navigateForwardButton.setIcon(QIcon("test.jpg"))
        self._navigateForwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self._navigateForwardButton.clicked.connect(self.showDetail)

        self._navigateUpButton = QToolButton()                                     
        self._navigateUpButton.setCheckable(True)                                  
        self._navigateUpButton.setChecked(False)                                   
        self._navigateUpButton.setArrowType(Qt.UpArrow)
        self._navigateUpButton.setAutoRaise(True)
        #self._navigateUpButton.setIcon(QIcon("test.jpg"))
        self._navigateUpButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._navigateUpButton.clicked.connect(self.navigateUp)

        splitter = QSplitter(Qt.Horizontal)

        self.addressBar = QLineEdit()
        self.addressBar.setMaxLength(255)
        splitter.addWidget(self.addressBar)

        self.searchField = QLineEdit()
        self.searchField.setMaxLength(30)
        splitter.addWidget(self.searchField)

        splitter.setStretchFactor(8, 1)
        splitter.setSizes([500, 200])


        self.toolbar.addWidget(self._navigateBackButton)
        self.toolbar.addWidget(self._navigateForwardButton)
        self.toolbar.addWidget(self._navigateUpButton)
        self.toolbar.addWidget(splitter)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")

    def selectAll(self):
        self.tree.selection_set(*self.tree.get_children())
    
    def unselectAll(self):
        self.tree.selection_set([])
    
    def navigate(self, index):
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath()
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))
        self.setWindowTitle(self.currentDir)
        self.addressBar.setText(self.currentDir)
    def navigateUp(self, event):
        self.currentDir = os.path.dirname(self.currentDir)
        self.navigate(self.mainModel.setRootPath(self.currentDir))
    def navigateFromSideTree(self, selected, unselected):
        print(selected)
    def createFile(self):
        x = tk.tkSimpleDialog.askstring
        return
    def deleteFiles(self, event):
        reply = QMessageBox.question(self, 'Delete', 'Are you sure you sure you want to delete those elements ?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if  reply == QMessageBox.Yes:
            for file in self.tree.selection():
                fileName = self.tree.item(file, "values")[0]
                filePath = join(self.currentDir, fileName)
                if os.path.exists(filePath):
                    try:
                        if isdir(filePath):
                            shutil.rmtree(filePath)
                        elif isfile(filePath):
                            os.remove(filePath) 
                        self.tree.delete(file)
                    except OSError:
                        print("failed to delete: " + filePath)
                        pass
                else:
                    self.tree.delete(file)

    def updateStatus(self):
        status = str(len(self.tree.get_children())) + " elements"
        if len(self.tree.selection()) > 0:
            status += " | " + str(len(self.tree.selection())) + " elements selected"
        
        self.statusBar().showMessage(status)
    def onDoubleClick(self, event):
        item = self.tree.identify('item',event.x,event.y)
        itemName = self.tree.item(item, "values")[0]
        itemPath = join(self.currentDir, itemName);
        if isdir(itemPath):
            print("you clicked on", itemName)
            self.navigate(join(self.currentDir, itemName))
        elif isfile(itemPath):
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', itemPath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(itemPath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', itemPath))
    def contextItemMenu(self, position): ################### Code for custom menu, this is the default for a QUIT menu
        menu = QMenu()
        newAction = menu.addAction("New")
        quitAction = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(position))
        if action == quitAction:
            sys.exit(app.exec_())

    def createTopMenu(self):
        # Add menus
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('&File')
        editMenu = menuBar.addMenu("&Edit")
        viewMenu = menuBar.addMenu("&View")
        goMenu = menuBar.addMenu("&Go")
        helpMenu = menuBar.addMenu("&Help")

        # File
        newAction = QAction('&New', self)        
        # newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New')

        exitAction = QAction('&Exit', self)        
        exitAction.setStatusTip('Exit')

        fileMenu.addAction(newAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        # Edit
        cutAction = QAction('&Cut', self)        
        # cutAction.setShortcut('Ctrl+X')
        cutAction.setStatusTip('Cut')

        copyAction = QAction('&Copy', self)        
        copyAction.setStatusTip('Copy')

        pasteAction = QAction('&Paste', self)        
        pasteAction.setStatusTip('Paste')

        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        # About
        aboutAction = QAction('&About', self)
        aboutAction.setStatusTip('About')
        helpMenu.addAction(aboutAction)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(Path.home())
    sys.exit(app.exec_()) 

