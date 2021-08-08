from PyQt5 import QtGui, QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.figure import Figure

class Ui_MainWindow():
    def setupUi(self, MainWindow):
        # Main window
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        MainWindow.setMinimumSize(QtCore.QSize(800, 480))
        MainWindow.setWindowIcon(QtGui.QIcon('ncviewer.ico'))
        MainWindow.setWindowTitle("ncviewer v0.5")

        # Central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        # Grid layout for central widget
        self.gridLayout = QtWidgets.QGridLayout()
        self.centralwidget.setLayout(self.gridLayout)

        # Menubar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        MainWindow.setMenuBar(self.menubar)

        # Menubar actions
        self.menuFile = QtWidgets.QMenu(MainWindow)
        self.menuFile.setTitle("File")
        self.menubar.addAction(self.menuFile.menuAction())

        self.menuView = QtWidgets.QMenu(MainWindow)
        self.menuView.setTitle("View")
        self.menubar.addAction(self.menuView.menuAction())

        self.menuStats = QtWidgets.QMenu(MainWindow)
        self.menuStats.setTitle("Stats")
        self.menubar.addAction(self.menuStats.menuAction())

        self.menuVisualize = QtWidgets.QMenu(MainWindow)
        self.menuVisualize.setTitle("Visualize")
        self.menubar.addAction(self.menuVisualize.menuAction())

        # Statusbar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # Menu File actions
        self.actionOpen = QtWidgets.QAction(MainWindow)
        self.actionOpen.setObjectName("actionOpen")
        self.actionOpen.setText("Open")
        self.menuFile.addAction(self.actionOpen)

        self.menuFile.addSeparator()

        self.actionSaveDataAsPNG = QtWidgets.QAction(MainWindow)
        self.actionSaveDataAsPNG.setObjectName("actionSaveDataAsPNG")
        self.actionSaveDataAsPNG.setText("Save data as png")
        self.actionSaveDataAsPNG.setEnabled(False)
        self.menuFile.addAction(self.actionSaveDataAsPNG)

        self.actionSaveFig = QtWidgets.QAction(MainWindow)
        self.actionSaveFig.setObjectName("actionSaveFig")
        self.actionSaveFig.setText("Save figure")
        self.actionSaveFig.setEnabled(False)
        self.menuFile.addAction(self.actionSaveFig)

        self.menuFile.addSeparator()

        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionExit.setText("Exit")
        self.menuFile.addAction(self.actionExit)

        # Menu View actions
        self.actionExpandTreeview = QtWidgets.QAction(MainWindow)
        self.actionExpandTreeview.setObjectName("actionExpandTreeview")
        self.actionExpandTreeview.setText("Expand treeview")
        self.menuView.addAction(self.actionExpandTreeview)

        self.actionCollapseTreeview = QtWidgets.QAction(MainWindow)
        self.actionCollapseTreeview.setObjectName("actionCollapseTreeview")
        self.actionCollapseTreeview.setText("Collapse treeview")
        self.menuView.addAction(self.actionCollapseTreeview)

        self.menuView.addSeparator()

        self.actionToggleText = QtWidgets.QAction(MainWindow)
        self.actionToggleText.setObjectName("actionToggleText")
        self.actionToggleText.setText("Toggle text editor")
        self.menuView.addAction(self.actionToggleText)

        self.actionClearText = QtWidgets.QAction(MainWindow)
        self.actionClearText.setObjectName("actionClearText")
        self.actionClearText.setText("Clear text")
        self.menuView.addAction(self.actionClearText)

        # Menu Stats actions
        self.actionCountMasked = QtWidgets.QAction(MainWindow)
        self.actionCountMasked.setObjectName("actionCountMasked")
        self.actionCountMasked.setText("Count masked")
        self.menuStats.addAction(self.actionCountMasked)

        self.actionCountNaN = QtWidgets.QAction(MainWindow)
        self.actionCountNaN.setObjectName("actionCountNaN")
        self.actionCountNaN.setText("Count NaN")
        self.menuStats.addAction(self.actionCountNaN)

        self.actionCountWhere = QtWidgets.QAction(MainWindow)
        self.actionCountWhere.setObjectName("actionCountWhere")
        self.actionCountWhere.setText("Count where...")
        self.menuStats.addAction(self.actionCountWhere)

        # Menu Visualize actions
        self.actionToggleGraph = QtWidgets.QAction(MainWindow)
        self.actionToggleGraph.setObjectName("actionToggleGraph")
        self.actionToggleGraph.setText("Toggle graph viewer")
        self.menuVisualize.addAction(self.actionToggleGraph)

        self.actionVisualSetup = QtWidgets.QAction(MainWindow)
        self.actionVisualSetup.setObjectName("actionVisualSetup")
        self.actionVisualSetup.setText("Visualization setup")
        self.menuVisualize.addAction(self.actionVisualSetup)

        self.menuVisualize.addSeparator()

        self.actionOriginal = QtWidgets.QAction(MainWindow)
        self.actionOriginal.setObjectName("actionOriginal")
        self.actionOriginal.setText("Original")
        self.actionOriginal.setEnabled(False)
        self.menuVisualize.addAction(self.actionOriginal)

        self.actionGradient = QtWidgets.QAction(MainWindow)
        self.actionGradient.setObjectName("actionGradient")
        self.actionGradient.setText("Sobel gradient")
        self.actionGradient.setEnabled(False)
        self.menuVisualize.addAction(self.actionGradient)

        self.actionSIEDFront = QtWidgets.QAction(MainWindow)
        self.actionSIEDFront.setObjectName("actionSIEDFront")
        self.actionSIEDFront.setText("SIED front")
        self.actionSIEDFront.setEnabled(False)
        self.menuVisualize.addAction(self.actionSIEDFront)

        # Size policy for some widgets
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Treeview
        self.treeWidget = QtWidgets.QTreeWidget()
        sizePolicy.setHorizontalStretch(1)
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setObjectName("treeView")
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabel("This nc file:")
        self.gridLayout.addWidget(self.treeWidget,0,0,2,1)

        # Welcome label
        self.welcomeLabel = QtWidgets.QLabel()
        sizePolicy.setHorizontalStretch(3)
        self.welcomeLabel.setSizePolicy(sizePolicy)
        self.welcomeLabel.setObjectName("welcomeLabel")
        self.welcomeLabel.setText("<font color=#0061A1>" +
            "<b>Open a netCDF file to check its contents.</b></font>")
        self.welcomeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.gridLayout.addWidget(self.welcomeLabel,0,1,2,1)

        # Text editor
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setHidden(True)
        self.gridLayout.addWidget(self.textEdit,0,1,2,1)

        # Canvas
        self.fig = Figure()
        self.fig.set_tight_layout(True)
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setObjectName("canvas")
        self.canvas.setSizePolicy(sizePolicy)
        self.canvas.setHidden(True)
        self.gridLayout.addWidget(self.canvas,0,1)

        # Navigation toolbar
        self.navToolbar = NavigationToolbar2QT(self.canvas,self.centralwidget)
        self.navToolbar.setObjectName("navToolbar")
        self.navToolbar.setHidden(True)
        self.gridLayout.addWidget(self.navToolbar,1,1)

        # Other
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

class Ui_CountMaskedOrNaN():
    def setupUi(self, Window, data):
        # Set common stuff
        self.setCommonStuff(Window, data)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.gridLayout.addWidget(self.buttonOK,2,0,1,2)

        QtCore.QMetaObject.connectSlotsByName(Window)
    
    def setCommonStuff(self, Window, data):
        Window.setObjectName("Window")
        Window.setWindowIcon(QtGui.QIcon('ncviewer.ico'))
        Window.setMinimumSize(QtCore.QSize(300, 150))
        self.gridLayout = QtWidgets.QGridLayout()
        Window.setLayout(self.gridLayout)

        self.labelSelectVar = QtWidgets.QLabel("Select a variable:")
        self.gridLayout.addWidget(self.labelSelectVar,0,0)

        self.comboBoxSelectVar = QtWidgets.QComboBox()
        self.comboBoxSelectVar.setObjectName("comboBoxSelectVar")
        self.comboBoxSelectVar.addItems(data.varNames)
        self.gridLayout.addWidget(self.comboBoxSelectVar,0,1)

        self.labelSubset = QtWidgets.QLabel("Subset " +
            str(data.obj.variables[self.comboBoxSelectVar.currentText()].dimensions))
        self.gridLayout.addWidget(self.labelSubset,1,0)

        self.lineEditSubset = QtWidgets.QLineEdit("(start, end, ...)")
        self.lineEditSubset.setObjectName("lineEditSubset")
        self.gridLayout.addWidget(self.lineEditSubset,1,1)

class Ui_CountWhere(Ui_CountMaskedOrNaN):
    def __init__(self):
        super().__init__()
    
    def setupUi(self, Window, data):
        # Set common stuff
        self.setCommonStuff(Window, data)

        self.labelMin = QtWidgets.QLabel("Min (inclusive)")
        self.gridLayout.addWidget(self.labelMin,2,0)

        self.lineEditMin = QtWidgets.QLineEdit("(Optional)",Window)
        self.lineEditMin.setObjectName("lineEditMin")
        self.gridLayout.addWidget(self.lineEditMin,2,1)

        self.labelMax = QtWidgets.QLabel("Max (inclusive)")
        self.gridLayout.addWidget(self.labelMax,3,0)

        self.lineEditMax = QtWidgets.QLineEdit("(Optional)",Window)
        self.lineEditMax.setObjectName("lineEditMax")
        self.gridLayout.addWidget(self.lineEditMax,3,1)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.gridLayout.addWidget(self.buttonOK,4,0,1,2)

        QtCore.QMetaObject.connectSlotsByName(Window)

class Ui_VisualSetup(Ui_CountMaskedOrNaN):
    def __init__(self):
        super().__init__()
    
    def setupUi(self, Window, data):
        # Set common stuff
        self.setCommonStuff(Window, data)

        # Add "None" option to the rest combobox.
        varNames = list(data.varNames)
        varNames.insert(0, "None")

        self.labelSelectLon = QtWidgets.QLabel("Select longitude:")
        self.gridLayout.addWidget(self.labelSelectLon,2,0)

        self.comboBoxSelectLon = QtWidgets.QComboBox()
        self.comboBoxSelectLon.setObjectName("comboBoxSelectLon")
        self.comboBoxSelectLon.addItems(varNames)
        self.gridLayout.addWidget(self.comboBoxSelectLon,2,1)

        self.labelSelectLat = QtWidgets.QLabel("Select latitude:")
        self.gridLayout.addWidget(self.labelSelectLat,3,0)

        self.comboBoxSelectLat = QtWidgets.QComboBox()
        self.comboBoxSelectLat.setObjectName("comboBoxSelectLat")
        self.comboBoxSelectLat.addItems(varNames)
        self.gridLayout.addWidget(self.comboBoxSelectLat,3,1)

        self.labelMin = QtWidgets.QLabel("Mask smaller than:")
        self.gridLayout.addWidget(self.labelMin,4,0)

        self.lineEditMin = QtWidgets.QLineEdit("(Optional)",Window)
        self.lineEditMin.setObjectName("lineEditMin")
        self.gridLayout.addWidget(self.lineEditMin,4,1)

        self.labelMax = QtWidgets.QLabel("Mask greater than:")
        self.gridLayout.addWidget(self.labelMax,5,0)

        self.lineEditMax = QtWidgets.QLineEdit("(Optional)",Window)
        self.lineEditMax.setObjectName("lineEditMax")
        self.gridLayout.addWidget(self.lineEditMax,5,1)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.gridLayout.addWidget(self.buttonOK,6,0,1,2)

        QtCore.QMetaObject.connectSlotsByName(Window)

class Ui_MedianFilterSize():
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.setWindowTitle("Set median filter size")
        Window.setWindowIcon(QtGui.QIcon('ncviewer.ico'))
        Window.setMinimumWidth(260)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        Window.setLayout(self.verticalLayout)

        self.labelMedianFilterSize = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelMedianFilterSize)

        self.hSliderFilterSize = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderFilterSize.setObjectName("hSliderFilterSize")
        self.hSliderFilterSize.setMinimum(1)
        self.hSliderFilterSize.setMaximum(35)
        self.hSliderFilterSize.setSingleStep(2)
        self.hSliderFilterSize.setValue(5)
        self.hSliderFilterSize.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderFilterSize)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.verticalLayout.addWidget(self.buttonOK)

        QtCore.QMetaObject.connectSlotsByName(Window)

class Ui_SIED():
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.setWindowTitle("SIED dashboard")
        Window.setWindowIcon(QtGui.QIcon('ncviewer.ico'))
        Window.setMinimumWidth(260)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        Window.setLayout(self.verticalLayout)

        self.labelMedianFilterSize = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelMedianFilterSize)

        self.hSliderFilterSize = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderFilterSize.setObjectName("hSliderFilterSize")
        self.hSliderFilterSize.setMinimum(1)
        self.hSliderFilterSize.setMaximum(35)
        self.hSliderFilterSize.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderFilterSize)

        self.labelWindowSize = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelWindowSize)

        self.hSliderWindowSize = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderWindowSize.setObjectName("hSliderWindowSize")
        self.hSliderWindowSize.setMaximum(8)
        self.hSliderWindowSize.setMaximum(256)
        self.hSliderWindowSize.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderWindowSize)

        self.labelWindowStride = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelWindowStride)

        self.hSliderWindowStride = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderWindowStride.setObjectName("hSliderWindowStride")
        self.hSliderWindowStride.setMinimum(4)
        self.hSliderWindowStride.setMaximum(128)
        self.hSliderWindowStride.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderWindowStride)

        self.labelNumTry = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelNumTry)

        self.hSliderNumTry = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderNumTry.setObjectName("hSliderNumTry")
        self.hSliderNumTry.setMinimum(8)
        self.hSliderNumTry.setMaximum(128)
        self.hSliderNumTry.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderNumTry)

        self.labelNumClass1 = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelNumClass1)

        self.hSliderNumClass1 = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderNumClass1.setObjectName("hSliderNumClass1")
        self.hSliderNumClass1.setMinimum(10)
        self.hSliderNumClass1.setMaximum(50)
        self.hSliderNumClass1.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderNumClass1)

        self.labelNumClass2 = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelNumClass2)

        self.hSliderNumClass2 = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderNumClass2.setObjectName("hSliderNumClass2")
        self.hSliderNumClass2.setMinimum(10)
        self.hSliderNumClass2.setMaximum(50)
        self.hSliderNumClass2.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderNumClass2)

        self.labelTheta = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelTheta)

        self.hSliderTheta = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderTheta.setObjectName("hSliderTheta")
        self.hSliderTheta.setMinimum(50)
        self.hSliderTheta.setMaximum(90)
        self.hSliderTheta.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderTheta)

        self.labelCohesionThr1 = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelCohesionThr1)

        self.hSliderCohesionThr1 = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderCohesionThr1.setObjectName("hSliderCohesionThr1")
        self.hSliderCohesionThr1.setMinimum(50)
        self.hSliderCohesionThr1.setMaximum(100)
        self.hSliderCohesionThr1.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderCohesionThr1)

        self.labelCohesionThr2 = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelCohesionThr2)

        self.hSliderCohesionThr2 = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderCohesionThr2.setObjectName("hSliderCohesionThr2")
        self.hSliderCohesionThr2.setMinimum(50)
        self.hSliderCohesionThr2.setMaximum(100)
        self.hSliderCohesionThr2.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderCohesionThr2)

        self.labelCohesionThrBoth = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelCohesionThrBoth)

        self.hSliderCohesionThrBoth = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderCohesionThrBoth.setObjectName("hSliderCohesionThrBoth")
        self.hSliderCohesionThrBoth.setMinimum(50)
        self.hSliderCohesionThrBoth.setMaximum(100)
        self.hSliderCohesionThrBoth.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderCohesionThrBoth)

        self.buttonResetPara = QtWidgets.QPushButton(text="Reset parameters",
            parent=Window)
        self.buttonResetPara.setObjectName("buttonResetPara")
        self.verticalLayout.addWidget(self.buttonResetPara)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.verticalLayout.addWidget(self.buttonOK)

        QtCore.QMetaObject.connectSlotsByName(Window)

class Ui_SaveFigure():
    def setupUi(self, Window):
        Window.setObjectName("Window")
        Window.setWindowTitle("Save current figure")
        Window.setWindowIcon(QtGui.QIcon('ncviewer.ico'))
        Window.setMinimumWidth(240)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        Window.setLayout(self.verticalLayout)

        self.labelDPI = QtWidgets.QLabel()
        self.verticalLayout.addWidget(self.labelDPI)

        self.hSliderDPI = QtWidgets.QSlider(QtCore.Qt.Horizontal, Window)
        self.hSliderDPI.setObjectName("hSliderDPI")
        self.hSliderDPI.setMinimum(50)
        self.hSliderDPI.setMaximum(600)
        self.hSliderDPI.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.verticalLayout.addWidget(self.hSliderDPI)

        self.buttonOK = QtWidgets.QPushButton(text="OK", parent=Window)
        self.buttonOK.setObjectName("buttonOK")
        self.verticalLayout.addWidget(self.buttonOK)

        QtCore.QMetaObject.connectSlotsByName(Window)