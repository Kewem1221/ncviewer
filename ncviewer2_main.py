import sys
from PyQt5 import QtWidgets, QtCore
from netCDF4 import Dataset
import cftime
import numpy as np
from numba import njit
from scipy.ndimage.filters import sobel, median_filter
from matplotlib.image import imsave

from ncviewer2_ui import *

@njit
def sied2(sst, winSize=16, stride=8, numTry=64, numClass1_threshold=0.3,
    numClass2_threshold=0.3, theta_threshold=0.7, cohesion1_threshold=0.87,
    cohesion2_threshold=0.87, cohesionBoth_threshold=0.89):
# SIED Cayula-Cornillon algorithm for detecting fronts in SST images.
# The original contour-following algorithm is not included.
    (height,width) = sst.shape
    front = np.zeros((height,width))
    for row in range(0,height-1,stride):
        for col in range(0,width-1,stride):
        # Defind window. tf = topleft, bf = bottomright.
        # We dont collect pixels on the image's edge.
            tl_y = row + 1
            tl_x = col + 1
            br_y = row + winSize
            br_x = col + winSize
            if br_y >= height - 1:
                br_y = height - 2
                tl_y = br_y - winSize + 1
            if br_x >= width - 1:
                br_x = width - 2
                tl_x = br_x - winSize + 1
        
            # This window's data and info
            data = sst[tl_y:br_y+1,tl_x:br_x+1].flatten()
            winMin = np.nanmin(data)
            winMax = np.nanmax(data)
            # Get possable segmenting thresholds.
            pst = np.linspace(winMin,winMax,numTry)
            # Histogram analysis
            theta = np.zeros(numTry)
            numClass1 = np.zeros(numTry)
            numClass2 = np.zeros(numTry)
            for i in range(len(pst)):
                # Class flag
                cf1 = data < pst[i]
                cf2 = data >= pst[i]
                # Number of pixels of cold watermass (class1) and
                # warm one (class2)
                numClass1[i] = np.nansum(cf1)
                numClass2[i] = np.nansum(cf2)
                # Check if we have enough data points.
                if (numClass1[i] < winSize ** 2 * numClass1_threshold or
                    numClass2[i] < winSize ** 2 * numClass2_threshold or
                    np.isnan(numClass1[i]) or
                    np.isnan(numClass2[i])):
                    continue
                # mean sst of class1 and class2
                meanTemp1 = np.nanmean(data[cf1])
                meanTemp2 = np.nanmean(data[cf2])
                # sst variance of class1 and class2
                variance1 = np.nanvar(data[cf1])
                variance2 = np.nanvar(data[cf2])
                # within-cluster variance (wcv)
                wcv = (numClass1[i] / (numClass1[i] + numClass2[i]) * variance1
                    + numClass2[i] / (numClass1[i] + numClass2[i]) * variance2)
            
                # between-cluster variance (bcv)
                bcv = (numClass1[i] * numClass2[i] / (numClass1[i] + numClass2[i])
                    * (meanTemp1 - meanTemp2) ** 2)
            
                # the ratio, denoted theta, used to decide whether one or two
                # populations are present
                theta[i] = bcv / (wcv + bcv)
            # Find max theta and its index.
            theta_idx = 0
            thetaMax = 0
            for currentTheta in theta:
                if currentTheta > thetaMax:
                    thetaMax = currentTheta
                    index = theta_idx
                theta_idx += 1
        
            # Now lets determine if this window pass the histogram analysis.
            if thetaMax >= theta_threshold:
                pst_opt = pst[index]
                numC1 = numClass1[index]
                numC2 = numClass2[index]
            else:
                continue
            # Cohesion test
            # r1: total number of comparisons between center pixels and neighbors
            # that both belong to population 1.
            r1 = 0
            # r2 is similarly defined.
            r2 = 0
            # Check only one neighbor (top)
            for y in range(tl_y,br_y+1):
                for x in range(tl_x,br_x+1):
                    # Count r1.
                    if sst[y,x] < pst_opt and sst[y-1,x] < pst_opt:
                        r1 += 1
                    # Count r2.
                    if sst[y,x] >= pst_opt and sst[y-1,x] >= pst_opt:
                        r2 += 1
        
            # Lets decide if the window pass the cohesion test.
            if (r1 / numC1 < cohesion1_threshold or
                r2 / numC2 < cohesion2_threshold or
                (r1 + r2) / (numC1 + numC2) < cohesionBoth_threshold):
                continue
            # Location of edge pixels
            # Mark pixels on warm side of the front, not two sides, as was
            # described in the paper.
            for y in range(tl_y,br_y+1):
                for x in range(tl_x,br_x+1):
                    if (sst[y,x] >= pst_opt and (
                        sst[y-1,x] < pst_opt or
                        sst[y+1,x] < pst_opt or
                        sst[y,x-1] < pst_opt or
                        sst[y,x+1] < pst_opt)):
                        front[y,x] = 1

    return front

class Data():
    def __init__(self, filename):
        self.obj = Dataset(filename)
        self.globalAttrNames = self.obj.ncattrs()
        self.varNames = self.obj.variables.keys()

        # Active variables for drawing
        self.image = "None"
        self.filtered = "None"
        self.activeImage = "None"
        self.lon = "None"
        self.lat = "None"
        self.mappable = None

class CountMaskedOrNaNWin(QtWidgets.QDialog, Ui_CountMaskedOrNaN):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent, data, winTitle):
        super().__init__(parent)
        self.setupUi(self, data)
        self.setWindowTitle(winTitle)
        self.show()
        self.data = data
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        self.varName = self.comboBoxSelectVar.currentText()
        self.subsetParameters = self.lineEditSubset.text()
        self.okSignal.emit()
    
    @QtCore.pyqtSlot(str)
    def on_comboBoxSelectVar_currentTextChanged(self, currentText):
        self.labelSubset.setText("Subset " +
            str(self.data.obj.variables[currentText].dimensions))

class CountWhereWin(QtWidgets.QDialog, Ui_CountWhere):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent, data, winTitle):
        super().__init__(parent)
        self.setupUi(self, data)
        self.setWindowTitle(winTitle)
        self.show()
        self.data = data
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        self.varName = self.comboBoxSelectVar.currentText()
        self.subsetParameters = self.lineEditSubset.text()
        self.varMin = self.lineEditMin.text()
        self.varMax = self.lineEditMax.text()
        self.okSignal.emit()
    
    @QtCore.pyqtSlot(str)
    def on_comboBoxSelectVar_currentTextChanged(self, currentText):
        self.labelSubset.setText("Subset " +
            str(self.data.obj.variables[currentText].dimensions))

class VisualSetupWin(QtWidgets.QDialog, Ui_VisualSetup):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent, data):
        super().__init__(parent)
        self.setupUi(self, data)
        self.setWindowTitle("Visualization setup")
        self.show()
        self.data = data
    
    @QtCore.pyqtSlot(str)
    def on_comboBoxSelectVar_currentTextChanged(self, currentText):
        self.labelSubset.setText("Subset " +
            str(self.data.obj.variables[currentText].dimensions))
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        # Get designated data, lon, lat.
        self.varName = self.comboBoxSelectVar.currentText()
        self.lonName = self.comboBoxSelectLon.currentText()
        self.latName = self.comboBoxSelectLat.currentText()

        # Subset parameters for visualization
        self.subsetParameters = None
        self.lonSubsetPara = "None"
        self.latSubsetPara = "None"

        self.visualSetup()
        self.okSignal.emit()
    
    def visualSetup(self):
        self.subsetParameters = self.lineEditSubset.text().split(",")

        if (self.lonName not in self.data.varNames or
            self.latName not in self.data.varNames):
            return

        # Get variable dimension names in order.
        dimensions = self.data.obj.variables[self.varName].dimensions

        # Set lon and lat subset parameters.
        for i in range(0, len(self.data.obj.variables[self.varName].shape) * 2, 2):
            # Tip: parameter's coresponding dimension == designated dimension(s)
            if dimensions[int(i / 2)] in self.data.obj.variables[self.lonName].dimensions:
                self.lonSubsetPara = self.subsetParameters[i:i + 2]
            if dimensions[int(i / 2)] in self.data.obj.variables[self.latName].dimensions:
                self.latSubsetPara = self.subsetParameters[i:i + 2]
class MFSizeWin(QtWidgets.QDialog, Ui_MedianFilterSize):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.labelMedianFilterSize.setText("Median filter size: " +
            str(self.hSliderFilterSize.value()))
        self.show()
    
    @QtCore.pyqtSlot(int)
    def on_hSliderFilterSize_valueChanged(self, value):
        self.labelMedianFilterSize.setText("Median filter size: " + str(value))
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        self.filterSize = self.hSliderFilterSize.value()
        self.okSignal.emit()

class Sied_dashboard(QtWidgets.QDialog, Ui_SIED):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.show()
        self.resetDashboard()
    
    def resetDashboard(self):
        self.hSliderFilterSize.setValue(5)
        self.hSliderWindowSize.setValue(16)
        self.hSliderWindowStride.setValue(8)
        self.hSliderNumTry.setValue(32)
        self.hSliderNumClass1.setValue(30)
        self.hSliderNumClass2.setValue(30)
        self.hSliderTheta.setValue(70)
        self.hSliderCohesionThr1.setValue(87)
        self.hSliderCohesionThr2.setValue(87)
        self.hSliderCohesionThrBoth.setValue(89)
    
    @QtCore.pyqtSlot(int)
    def on_hSliderFilterSize_valueChanged(self, value):
        self.labelMedianFilterSize.setText("Median filter size: " + str(value))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderWindowSize_valueChanged(self, value):
        self.labelWindowSize.setText("Window size: " + str(value))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderWindowStride_valueChanged(self, value):
        self.labelWindowStride.setText("Window stride: " + str(value))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderNumTry_valueChanged(self, value):
        self.labelNumTry.setText("Number of try: " + str(value))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderNumClass1_valueChanged(self, value):
        self.labelNumClass1.setText("Class 1 ratio: " + str(value / 100))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderNumClass2_valueChanged(self, value):
        self.labelNumClass2.setText("Class 2 ratio: " + str(value / 100))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderTheta_valueChanged(self, value):
        self.labelTheta.setText("Histogram analysis threshold: " + str(value / 100))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderCohesionThr1_valueChanged(self, value):
        self.labelCohesionThr1.setText("Cohesion threshold (class 1): " + str(value / 100))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderCohesionThr2_valueChanged(self, value):
        self.labelCohesionThr2.setText("Cohesion threshold (class 2): " + str(value / 100))
    
    @QtCore.pyqtSlot(int)
    def on_hSliderCohesionThrBoth_valueChanged(self, value):
        self.labelCohesionThrBoth.setText("Cohesion threshold (both): " + str(value / 100))
    
    @QtCore.pyqtSlot()
    def on_buttonResetPara_clicked(self):
        self.resetDashboard()
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        self.okSignal.emit()

class SaveFigWin(QtWidgets.QDialog, Ui_SaveFigure):
    okSignal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.show()
        self.hSliderDPI.setValue(100)
    
    @QtCore.pyqtSlot(int)
    def on_hSliderDPI_valueChanged(self, value):
        self.labelDPI.setText("DPI: " + str(value))
    
    @QtCore.pyqtSlot()
    def on_buttonOK_clicked(self):
        self.okSignal.emit()

class MainWindom(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.show()

        # Signals and Slots
        self.treeWidget.itemClicked.connect(self.printAttribute)
    
    @QtCore.pyqtSlot()
    def on_actionExit_triggered(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_actionExpandTreeview_triggered(self):
        self.treeWidget.expandAll()

    @QtCore.pyqtSlot()
    def on_actionCollapseTreeview_triggered(self):
        self.treeWidget.collapseAll()
    
    @QtCore.pyqtSlot()
    def on_actionToggleText_triggered(self):
        self.toggleText()
    
    @QtCore.pyqtSlot()
    def on_actionClearText_triggered(self):
        self.textEdit.clear()
    
    @QtCore.pyqtSlot()
    def on_actionToggleGraph_triggered(self):
        self.toggleGraph()
    
    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        # Get selected filename.
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a nc file",
            "C:\\", "nc files (*.nc *.nc4)")
        
        # Open nc file.
        if filename:
            try:
                self.statusbar.showMessage(filename)
                self.data = Data(filename)
                self.updateTreeWidget()
            except:
                self.statusbar.showMessage("Oops! We have a problem opening your file")
    
    @QtCore.pyqtSlot()
    def on_actionCountMasked_triggered(self):
        try:
            # Open parameter window
            self.countMaskedOrNaNWin = CountMaskedOrNaNWin(self, self.data,
                "Count masked")
            self.countMaskedOrNaNWin.okSignal.connect(self.countMasked)
        except:
            self.statusbar.showMessage("No variables.")
    
    @QtCore.pyqtSlot()
    def on_actionCountNaN_triggered(self):
        try:
            # Open parameter window
            self.countMaskedOrNaNWin = CountMaskedOrNaNWin(self, self.data,
                "Count NaN")
            self.countMaskedOrNaNWin.okSignal.connect(self.countNaN)
        except:
            self.statusbar.showMessage("No variables.")
    
    @QtCore.pyqtSlot()
    def on_actionCountWhere_triggered(self):
        try:
            # Open parameter window
            self.countWhereWin = CountWhereWin(self, self.data,
                "Count Where...")
            self.countWhereWin.okSignal.connect(self.countWhere)
        except:
            self.statusbar.showMessage("No variables.")
    
    @QtCore.pyqtSlot()
    def on_actionVisualSetup_triggered(self):
        try:
            # Open parameter window
            self.visualSetupWin = VisualSetupWin(self, self.data)
            self.visualSetupWin.okSignal.connect(self.prepareDataToDraw)
        except:
            self.statusbar.showMessage("No variables.")
    
    @QtCore.pyqtSlot()
    def on_actionOriginal_triggered(self):
        # Open parameter window
        self.mfSizeWin = MFSizeWin(self)
        self.mfSizeWin.okSignal.connect(self.drawOriginal)
    
    @QtCore.pyqtSlot()
    def on_actionGradient_triggered(self):
        # Open parameter window
        self.mfSizeWin = MFSizeWin(self)
        self.mfSizeWin.okSignal.connect(self.drawGradient)
    
    @QtCore.pyqtSlot()
    def on_actionSIEDFront_triggered(self):
        # Open dashboard window
        self.sied_dashboard = Sied_dashboard(self)
        self.sied_dashboard.okSignal.connect(self.drawSIEDfront)
    
    @QtCore.pyqtSlot()
    def on_actionSaveFig_triggered(self):
        self.saveFigWin = SaveFigWin(self)
        self.saveFigWin.okSignal.connect(self.saveFig)
    
    @QtCore.pyqtSlot()
    def on_actionSaveDataAsPNG_triggered(self):
        if isinstance(self.data.activeImage, str):
            self.statusbar.showMessage("No active image yet.")
            return
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save figure as",
            "C:\\", "pictures (*.png)")
        cmap = self.data.mappable.get_cmap()
        vmin, vmax = self.data.mappable.get_clim()
        imsave(filename, self.data.activeImage, vmin, vmax, cmap, 'png')
        
    
    def toggleText(self):
        self.welcomeLabel.setHidden(True)
        self.canvas.setHidden(True)
        self.navToolbar.setHidden(True)
        self.textEdit.setHidden(False)
    
    def toggleGraph(self):
        self.welcomeLabel.setHidden(True)
        self.canvas.setHidden(False)
        self.navToolbar.setHidden(False)
        self.textEdit.setHidden(True)

    def updateTreeWidget(self):
        self.treeWidget.clear()

        # Add global attribute branch
        globalAttrs = QtWidgets.QTreeWidgetItem(self.treeWidget)
        globalAttrs.setText(0, 'Global attributes')

        # Add variable branch
        variables = QtWidgets.QTreeWidgetItem(self.treeWidget)
        variables.setText(0, 'Variables')

        # Add global attributes' names.
        for globalAttrName in self.data.globalAttrNames:
            item = QtWidgets.QTreeWidgetItem(globalAttrs)
            item.setText(0, globalAttrName)

        # Add variable names.
        for varName in self.data.varNames:
            item = QtWidgets.QTreeWidgetItem(variables)
            item.setText(0, varName)

            # Add variable attributes' names.
            for attrName in self.data.obj.variables[varName].ncattrs():
                sub_item = QtWidgets.QTreeWidgetItem(item)
                sub_item.setText(0, attrName)
    
    def printAttribute(self, item, column):
        # Toggle text editor.
        self.toggleText()

        # get parent name
        try:
            parentName = item.parent().text(column)
        except:
            parentName = None
        # Get item name
        attrName = item.text(column)

        # Print attributes.
        # Check if the item is a variable.
        if parentName == 'Variables':
            self.textEdit.append(attrName + ' >> '
                +str(self.data.obj.variables[attrName]))
            
        # Check if the item is a global attribute.
        elif parentName == 'Global attributes':
            self.textEdit.append(attrName + ' >> ' +
                str(self.data.obj.getncattr(attrName)))
            
        # The item can still be a variable's attribute.
        elif parentName:
            self.textEdit.append(parentName +' >> ' + attrName + ' >> '
                + str(self.data.obj.variables[parentName].getncattr(attrName)))
            
        else:
            self.textEdit.append('This item has no value.')
        
        # Make next row empty.
        self.textEdit.append('')

    def subsetData(self, varName, subsetParameters):
        # Get subset parameters from user-input text.
        if isinstance(subsetParameters, str):
            subsetParameters = subsetParameters.split(",")
            p = [int(para) for para in subsetParameters]
        else:
            p = [int(para) for para in subsetParameters]
        
        numDims = len(self.data.obj.variables[varName].shape)

        # Subset original variable.
        if len(p) / 2 == 1 and numDims == 1:
            data = self.data.obj.variables[varName][p[0]:p[1]]
        if len(p) / 2 == 2 and numDims == 2:
            data = self.data.obj.variables[varName][p[0]:p[1], p[2]:p[3]]
        if len(p) / 2 == 3 and numDims == 3:
            data = np.squeeze(self.data.obj.variables[varName][p[0]:p[1], p[2]:p[3],
                p[4]:p[5]])
        if len(p) / 2 == 4 and numDims == 4:
            data = np.squeeze(self.data.obj.variables[varName][p[0]:p[1], p[2]:p[3],
                p[4]:p[5], p[6]:p[7]])

        return data
    
    def countMasked(self):
        try:
            data = self.subsetData(self.countMaskedOrNaNWin.varName,
                self.countMaskedOrNaNWin.subsetParameters)
        except:
            data = self.data.obj.variables[self.countMaskedOrNaNWin.varName][...]
        
        if 0 in data.shape:
            self.statusbar.showMessage("Subset result is empty.")
            return
            
        numberMasked = np.ma.count_masked(data)
        numberTotal = 1
        for dim_length in data.shape:
            numberTotal *= dim_length

        self.textEdit.append("Mask count for " + self.countMaskedOrNaNWin.varName + " :")
        self.textEdit.append(str(numberMasked) + " masked")
        self.textEdit.append(str(numberTotal) + " total")
        self.textEdit.append("masked / total = " + str(numberMasked / numberTotal))
        self.textEdit.append("")
        self.toggleText()
    
    def countNaN(self):
        try:
            data = self.subsetData(self.countMaskedOrNaNWin.varName,
                self.countMaskedOrNaNWin.subsetParameters)
        except:
            data = self.data.obj.variables[self.countMaskedOrNaNWin.varName][...]
        
        if 0 in data.shape:
            self.statusbar.showMessage("Subset result is empty.")
            return

        numberNaN = np.sum(np.isnan(data))
        numberTotal = 1
        for dim_length in data.shape:
            numberTotal *= dim_length

        self.textEdit.append("NaN count for " + self.countMaskedOrNaNWin.varName + " :")
        self.textEdit.append(str(numberNaN) + " NaN")
        self.textEdit.append(str(numberTotal) + " total")
        self.textEdit.append("NaN / total = " + str(numberNaN / numberTotal))
        self.textEdit.append("")
        self.toggleText()
    
    def countWhere(self):
        try:
            data = self.subsetData(self.countWhereWin.varName,
                self.countWhereWin.subsetParameters)
        except:
            data = self.data.obj.variables[self.countWhereWin.varName][...]

        if 0 in data.shape:
            self.statusbar.showMessage("Subset result is empty.")
            return
        
        try:
            varMin = float(self.countWhereWin.varMin)
        except:
            varMin = None
        try:
            varMax = float(self.countWhereWin.varMax)
        except:
            varMax = None
        
        if varMin and varMax:
            numberWhere = np.sum(data>=varMin) - np.sum(data>varMax)
        elif varMin and varMax == None:
            numberWhere = np.sum(data>=varMin)
        elif varMin == None and varMax:
            numberWhere = np.sum(data<=varMax)
        else:
            # No limit is specified. Count NaN and mask.
            numberWhere = np.ma.count_masked(np.ma.masked_invalid(data))
        numberTotal = 1
        for dim_length in data.shape:
            numberTotal *= dim_length

        self.textEdit.append("Conditional count for " + self.countWhereWin.varName + " :")
        self.textEdit.append(str(numberWhere) + " meet the condition")
        self.textEdit.append(str(numberTotal) + " total")
        self.textEdit.append("conditional count / total = " + str(numberWhere / numberTotal))
        self.textEdit.append("")
        self.toggleText()
    
    def prepareDataToDraw(self):
        # Reset draw actions to disable.
        self.actionOriginal.setEnabled(False)
        self.actionGradient.setEnabled(False)
        self.actionSIEDFront.setEnabled(False)
        self.actionSaveDataAsPNG.setEnabled(False)
        self.actionSaveFig.setEnabled(False)

        # Reset active drawing data to "None".
        self.data.image = "None"
        self.data.lon = "None"
        self.data.lat = "None"

        try:
            data = self.subsetData(self.visualSetupWin.varName,
                self.visualSetupWin.subsetParameters)
            if 0 in data.shape:
                self.statusbar.showMessage("Subset result is empty.")
                return
            if len(data.shape) != 2:
                self.statusbar.showMessage("Data for drawing must be a 2D array.")
                return

            # Let's see if there are values to mask.
            # This step will convert masked values to nan cuz scipy is not compatible with mask.
            try: data[data.mask] = np.nan
            except: pass
            try: data[data < float(self.visualSetupWin.lineEditMin.text())] = np.nan
            except: pass
            try: data[data > float(self.visualSetupWin.lineEditMax.text())] = np.nan
            except: pass

            self.data.image = data

            # Now that we have data to draw, enable these actions.
            self.actionOriginal.setEnabled(True)
            self.actionGradient.setEnabled(True)
            self.actionSIEDFront.setEnabled(True)
            self.actionSaveDataAsPNG.setEnabled(True)
            self.actionSaveFig.setEnabled(True)

            # See if geographic coordinates are available.
            lon = self.subsetData(self.visualSetupWin.lonName,
                self.visualSetupWin.lonSubsetPara)
            if 0 in lon.shape:
                return
            self.data.lon = lon

            lat = self.subsetData(self.visualSetupWin.latName,
                self.visualSetupWin.latSubsetPara)
            if 0 in lat.shape:
                return
            self.data.lat = lat

            self.statusbar.showMessage(":) Visualization setup is all done.")
        except:
            self.statusbar.showMessage("Warning: visualization setup may be incomplete.")
    
    def drawGradient(self):
        # Apply designated filter.
        self.data.filtered = median_filter(self.data.image, self.mfSizeWin.filterSize)

        # Create gradient data.
        self.data.activeImage = np.sqrt(sobel(self.data.filtered, axis=0)**2 +
            sobel(self.data.filtered, axis=1)**2)

        # Draw
        self.pcolor(self.data.activeImage)
    
    def drawOriginal(self):
        # Apply designated filter.
        self.data.activeImage = median_filter(self.data.image, self.mfSizeWin.filterSize)

        # Draw
        self.pcolor(self.data.activeImage)

    def pcolor(self, array_2D):
        # Get last used colormap.
        if self.data.mappable:
            cmap = self.data.mappable.get_cmap()
        else:
            cmap = 'viridis'
        
        # Make space for drawing.
        self.fig.clear()
        axes = self.fig.add_subplot()

        # Switch to graph viewer.
        self.toggleGraph()

        # Draw
        if isinstance(self.data.lon, str) or isinstance(self.data.lat, str):
            self.data.mappable = axes.pcolormesh(array_2D, cmap=cmap, shading='auto')
        else:
            self.data.mappable = axes.pcolormesh(self.data.lon, self.data.lat,
                array_2D, cmap=cmap, shading='auto')

        # Add colorbar.
        self.fig.colorbar(self.data.mappable, ax=axes)
        
        # Add this to refresh the figure cuz it doesn't seem to
        # refresh itself when the drawing is done.
        self.fig.canvas.draw()
    
    def drawSIEDfront(self):
        # Apply designated filter.
        self.data.filtered = median_filter(self.data.image,
            self.sied_dashboard.hSliderFilterSize.value())
        
        # Detect fronts with SIED
        flag = sied2(self.data.filtered,
            self.sied_dashboard.hSliderWindowSize.value(),
            self.sied_dashboard.hSliderWindowStride.value(),
            self.sied_dashboard.hSliderNumTry.value(),
            self.sied_dashboard.hSliderNumClass1.value() / 100,
            self.sied_dashboard.hSliderNumClass2.value() / 100,
            self.sied_dashboard.hSliderTheta.value() / 100,
            self.sied_dashboard.hSliderCohesionThr1.value() / 100,
            self.sied_dashboard.hSliderCohesionThr2.value() / 100,
            self.sied_dashboard.hSliderCohesionThrBoth.value() / 100)
        
        # Suppress non-front pixels.
        self.data.activeImage = self.data.filtered
        self.data.activeImage[~flag.astype(np.bool)] = np.nan

        # Draw.
        self.pcolor(self.data.activeImage)
    
    def saveFig(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save figure as",
            "C:\\", "pictures (*.png *.jpg *.jpeg)")
        self.fig.savefig(filename, dpi=self.saveFigWin.hSliderDPI.value())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindom()
    sys.exit(app.exec())