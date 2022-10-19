from copy import copy
import shutil
from pathlib import Path
from os.path import isfile, isdir, join
import subprocess, os, platform
from PyQt5.QtWidgets import QApplication, QStyle, QAbstractItemView, QLineEdit, QTableView, QSplitter, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,QToolButton, QMenu, QWidget, QAction,QMessageBox, QDirModel, QFileSystemModel, QTreeView, QListView, QGridLayout, QFrame, QLabel, QDialogButtonBox, QDialog
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtCore import Qt,QDir, QVariant, QSize, QModelIndex
import sys

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About")
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel("Made by Antonin Desfontaines.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class App(QMainWindow):

    def __init__(self, initialDir):
        super().__init__()
        
        # Variables
        self.currentDir = initialDir
        self.history = {}
        self.mainExplorer = None
        # App init
        self.initUI()
    def initUI(self):
        # Status bar
        self.statusBar()
        
        # Dir model
        dirModel = QFileSystemModel()
        dirModel.setFilter(QDir.Dirs | QDir.NoDotAndDotDot)
        dirModel.setRootPath(QDir.rootPath())

        # Side explorer
        self.sideExplorer = QTreeView()
        self.sideExplorer.setModel(dirModel)
        self.sideExplorer.hideColumn(3)
        self.sideExplorer.hideColumn(2)
        self.sideExplorer.hideColumn(1)
        self.sideExplorer.header().hide()
        self.sideExplorer.clicked.connect(self.navigate)
        self.sideExplorer.setFrameStyle(QFrame.NoFrame)
        self.sideExplorer.uniformRowHeights = True

        self.mainModel = QFileSystemModel()
        self.mainModel.setRootPath(QDir.rootPath())
        self.mainModel.setReadOnly(False)
        self.mainModel.directoryLoaded.connect(self.updateStatus)
        # Main explorer
        self.changeView("Details")
        
        # Set layout and views
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        explorerLayout = QHBoxLayout()
        explorerLayout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(explorerLayout)

        self.explorerSplitter = QSplitter(Qt.Horizontal)
        self.explorerSplitter.addWidget(self.sideExplorer)
        self.explorerSplitter.addWidget(self.mainExplorer)

        self.explorerSplitter.setStretchFactor(1, 2)
        self.explorerSplitter.setSizes([400, 800])
        explorerLayout.addWidget(self.explorerSplitter)

        # Top menus
        self.createTopMenu()
        self.createActionBar()


        # Main widget
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.contextItemMenu) 
        self.setWindowIcon(QIcon('./src/ico/application-sidebar.png'))
        self.setLayout(layout)
        self.setGeometry(800,600,600,560)
        self.navigate(self.mainModel.setRootPath(QDir.homePath()))
        self.show()
    def about(self, event):
        dlg = AboutDialog(self)
        if dlg.exec():
            print("Success!")
        else:
            print("Cancel!")
    def createActionBar(self):
        
        self.toolbar = self.addToolBar("actionToolBar")
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        self._navigateBackButton = QToolButton()                                     
        self._navigateBackButton.setIcon(QIcon("./src/ico/arrow-180.png"))
        self._navigateBackButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        # self._navigateBackButton.clicked.connect(self.showDetail)

        self._navigateForwardButton = QToolButton()                                     
        self._navigateForwardButton.setIcon(QIcon("./src/ico/arrow.png"))
        self._navigateForwardButton.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self._navigateUpButton = QToolButton()                              
        self._navigateUpButton.setIcon(QIcon("./src/ico/arrow-090.png"))
        self._navigateUpButton.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._navigateUpButton.clicked.connect(self.navigateUp)

        splitter = QSplitter(Qt.Horizontal)

        self.addressBar = QLineEdit()
        self.addressBar.setMaxLength(255)
        splitter.addWidget(self.addressBar)

        self.searchField = QLineEdit()
        self.searchField.setPlaceholderText("Search")
        splitter.addWidget(self.searchField)

        splitter.setStretchFactor(10    , 1)
        splitter.setSizes([500, 200])


        self.toolbar.addWidget(self._navigateBackButton)
        self.toolbar.addWidget(self._navigateForwardButton)
        self.toolbar.addWidget(self._navigateUpButton)
        self.toolbar.addWidget(splitter)
        self.toolbar.setStyleSheet("QToolBar { border: 0px }")

    def selectAll(self, event):
        self.mainExplorer.selectAll()
    def unselectAll(self):
        self.mainExplorer.selectionModel().clearSelection()
    def navigate(self, index):
        self.currentDir = self.mainModel.fileInfo(index).absoluteFilePath()
        self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))
        self.setWindowTitle(os.path.basename(self.currentDir))
        self.addressBar.setText(self.currentDir)
    def navigateUp(self, event):
        self.currentDir = os.path.dirname(self.currentDir)
        self.navigate(self.mainModel.setRootPath(self.currentDir))
    def navigateFromSideTree(self, selected, unselected):
        print(selected)
    def deleteFiles(self, event):
        reply = QMessageBox.question(self, 'Delete', 'Are you sure you sure you want to delete those elements ?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if  reply == QMessageBox.Yes:
            selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes();
            for file in selectedIndexes:
                fileName = self.mainModel.itemData(file)[0]
                filePath = join(self.currentDir, fileName)
                if os.path.exists(filePath):
                    try:
                        if isdir(filePath):
                            shutil.rmtree(filePath)
                        elif isfile(filePath):
                            os.remove(filePath) 
                        self.mainModel.remove(file)
                    except OSError:
                        print("failed to delete: " + filePath)
                        pass
                else:
                    self.mainModel.remove(file)
    def changeView(self, view):
        if(view == "List"):
            if type(self.mainExplorer) is not QListView:
                self.mainExplorer = QListView()

            self.mainExplorer.setViewMode(QListView.ListMode)
            self.mainExplorer.setIconSize(QSize(64, 64))
        elif(view == "Icons"):
            if type(self.mainExplorer) is not QListView:
                self.mainExplorer = QListView()

            self.mainExplorer.setViewMode(QListView.IconMode)
            self.mainExplorer.setWordWrap(True)
            self.mainExplorer.setIconSize(QSize(64, 80))
            # self.mainExplorer.setGridSize(QSize(150, 150));
            self.mainExplorer.setUniformItemSizes(True)
        elif(view == "Details"):
            self.mainExplorer = QTableView()
            self.mainExplorer.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.mainExplorer.setSelectionMode(QAbstractItemView.ExtendedSelection)

            self.mainExplorer.verticalHeader().hide()
            self.mainExplorer.setShowGrid(False)
            self.mainExplorer.horizontalHeader().setSectionsMovable(True)
            self.mainExplorer.horizontalHeader().setHighlightSections(False)
            self.mainExplorer.setFrameStyle(QFrame.NoFrame)
            self.mainExplorer.setSortingEnabled(True)
            self.mainExplorer.setEditTriggers(QAbstractItemView.EditKeyPressed)

        # Common
        self.mainExplorer.doubleClicked.connect(self.onDoubleClick)
        self.mainExplorer.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mainExplorer.customContextMenuRequested.connect(self.contextItemMenu)
        self.mainExplorer.setModel(self.mainModel)

        if hasattr(self, "explorerSplitter"):
            self.explorerSplitter.replaceWidget(1, self.mainExplorer)
            self.mainExplorer.setRootIndex(self.mainModel.setRootPath(self.currentDir))


    def updateStatus(self, path):
        status = str(self.mainModel.rowCount(self.mainModel.index(path))) + " elements"
        selectedCount = len(self.mainExplorer.selectionModel().selectedIndexes())
        if selectedCount > 0:      
            status += " | " + str(selectedCount) + " elements selected"
        
        self.statusBar().showMessage(status)
    def onKeyPress(self, key):
        if key.key() == Qt.Key_Delete:
            self.deleteFiles(None)
    def onDoubleClick(self, event):
        itemPath = self.mainModel.fileInfo(event)

        if isdir(itemPath):
            self.navigate(event)
        elif isfile(itemPath):
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', itemPath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(itemPath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', itemPath))
    def contextItemMenu(self, position):
        index = self.mainExplorer.indexAt(position)
        if (index.isValid()):
            menu = QMenu()
            cutAction = menu.addAction("Cut")
            cutAction.triggered.connect(self.cutFiles)

            deleteAction = menu.addAction("Delete")
            deleteAction.triggered.connect(self.deleteFiles)
            
            renameAction = menu.addAction("Rename")
            renameAction.triggered.connect(self.renameFile)

            copyAction = menu.addAction("Copy")
            copyAction.triggered.connect(self.copyFiles)
            menu.addSeparator()
            # menu.addSeparator()
            # menu.addAction("Properties")
            action = menu.exec_(QCursor.pos())
        else:
            menu = QMenu()
            menu.addAction("Refresh")
            menu.addSeparator()
            pasteAction = menu.addAction("Paste")
            pasteAction.triggered.connect(self.pasteFiles)

            action = menu.exec_(QCursor.pos())
    def cutFiles(self, event):
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def copyFiles(self, event):
        self.selectedFiles = self.mainExplorer.selectionModel().selectedIndexes()
    def pasteFiles(self, event):
        for file in self.selectedFiles:
            fileName = self.mainModel.itemData(file)[0]
            filePath = join(self.currentDir, fileName)
            if os.path.exists(filePath):
                try:
                    shutil.copy(filePath, self.currentDir)
                    # self.mainModel.remove(file)
                except OSError:
                    print("failed to copy: " + filePath)
                    pass
            else:
                self.mainModel.remove(file)
    def renameFile(self, event):
        selectedIndexes = self.mainExplorer.selectionModel().selectedIndexes();
        for file in selectedIndexes:
            fileName = self.mainModel.itemData(file)[0]
            filePath = join(self.currentDir, fileName)
            if os.path.exists(filePath):
                self.mainExplorer.edit(file)
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

        selectAllAction = QAction('&Select All', self)
        selectAllAction.setStatusTip('Select All')
        selectAllAction.triggered.connect(self.selectAll)

        unselectAllAction = QAction('&Unselect All', self)
        unselectAllAction.setStatusTip('Unselect All')
        unselectAllAction.triggered.connect(self.unselectAll)

        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)
        editMenu.addSeparator()
        editMenu.addAction(selectAllAction)
        editMenu.addAction(unselectAllAction)
        
        # View
        iconsViewAction = QAction('&Icons', self)        
        iconsViewAction.setStatusTip('Icons')
        iconsViewAction.triggered.connect(lambda checked: self.changeView("Icons"))

        listViewAction = QAction('&List', self)        
        listViewAction.setStatusTip('List')
        listViewAction.triggered.connect(lambda checked: self.changeView("List"))

        detailViewAction = QAction('&Details', self)
        detailViewAction.setStatusTip('Details')
        detailViewAction.triggered.connect(lambda checked: self.changeView("Details"))

        viewMenu.addAction(iconsViewAction)
        viewMenu.addAction(listViewAction)
        viewMenu.addAction(detailViewAction)
        # About
        aboutAction = QAction('&About', self)
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.about)

        helpMenu.addAction(aboutAction)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App(Path.home())
    sys.exit(app.exec_()) 
