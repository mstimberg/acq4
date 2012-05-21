# -*- coding: utf-8 -*-

import time, types, os.path, re, sys
from PyQt4 import QtGui, QtCore
from CameraTemplate import Ui_MainWindow
import pyqtgraph as pg
from pyqtgraph import SignalProxy, Point
import ptime
#from lib.filetypes.ImageFile import *
from Mutex import Mutex, MutexLocker
import numpy as np
import scipy.ndimage
from debug import *
import debug
from metaarray import *
import lib.Manager as Manager
from RecordThread import RecordThread
from lib.LogWindow import LogButton
from StatusBar import StatusBar

traceDepth = 0
def trace(func):
    #def newFunc(*args, **kargs):
        #global traceDepth
        #print "  "*traceDepth + func.__name__
        #traceDepth += 2
        #ret = func(*args, **kargs)
        #traceDepth -= 2
        #print "  "*traceDepth + func.__name__, "done"
        #return ret
    #return newFunc
    return func


class CamROI(pg.ROI):
    def __init__(self, size, parent=None):
        pg.ROI.__init__(self, pos=[0,0], size=size, maxBounds=QtCore.QRectF(0, 0, size[0], size[1]), scaleSnap=True, translateSnap=True, parent=parent)
        self.addScaleHandle([0, 0], [1, 1])
        self.addScaleHandle([1, 0], [0, 1])
        self.addScaleHandle([0, 1], [1, 0])
        self.addScaleHandle([1, 1], [0, 0])

class PlotROI(pg.ROI):
    def __init__(self, pos, size):
        pg.ROI.__init__(self, pos, size=size)
        self.addScaleHandle([1, 1], [0, 0])


        
        
class CameraWindow(QtGui.QMainWindow):
    
    sigCameraPosChanged = QtCore.Signal()
    sigCameraScaleChanged = QtCore.Signal()
    
    def __init__(self, module):
        self.hasQuit = False
        self.module = module ## handle to the rest of the application
        
        ## Camera state variables
        self.cam = self.module.cam
        self.roi = None
        self.exposure = 0.001
        self.binning = 1
        self.region = None
        
        ## ROI state variables
        self.lastPlotTime = None
        self.ROIs = []
        self.plotCurves = []
        
        ## Frame handling variables
        self.nextFrame = None
        self.updateFrame = False
        self.currentFrame = None
        #self.currentClipMask = None
        self.backgroundFrame = None
        self.blurredBackgroundFrame = None
        self.lastDrawTime = None
        #self.fps = None
        #self.displayFps = None
        self.bgStartTime = None
        self.bgFrameCount = 0
        #self.levelMax = 1
        #self.levelMin = 0
        self.lastMinMax = None  ## Records most recently measured maximum/minimum image values
        #self.AGCLastMax = None
        self.autoGainLevels = [0.0, 1.0]
        self.ignoreLevelChange = False
        self.persistentFrames = []
        
        
        ## Start building UI
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #self.setCentralWidget(self.ui.centralwidget)
        
        ## Load previous window state
        self.stateFile = os.path.join('modules', self.module.name + '_ui.cfg')
        uiState = module.manager.readConfigFile(self.stateFile)
        if 'geometry' in uiState:
            geom = QtCore.QRect(*uiState['geometry'])
            self.setGeometry(geom)
        if 'window' in uiState:
            ws = QtCore.QByteArray.fromPercentEncoding(uiState['window'])
            self.restoreState(ws)
        
        ## set up ViewBox
        #self.ui.graphicsView.useOpenGL(True)  ## a bit buggy, but we need the speed.
        self.view = pg.ViewBox()
        self.view.setAspectLocked(True)
        #self.view.invertY()
        self.ui.graphicsView.setCentralItem(self.view)
        
        ## set up item groups
        self.scopeItemGroup = pg.ItemGroup()   ## translated as scope moves
        self.cameraItemGroup = pg.ItemGroup()  ## translated with scope, scaled with camera objective
        self.imageItemGroup = pg.ItemGroup()   ## translated and scaled as each frame arrives
        self.view.addItem(self.imageItemGroup)
        self.view.addItem(self.cameraItemGroup)
        self.view.addItem(self.scopeItemGroup)
        self.scopeItemGroup.setZValue(10)
        self.cameraItemGroup.setZValue(0)
        self.imageItemGroup.setZValue(0)
        
        ## video image item
        self.imageItem = pg.ImageItem()
        self.view.addItem(self.imageItem)
        self.imageItem.setParentItem(self.imageItemGroup)
        self.imageItem.setZValue(-10)
        self.ui.histogram.setImageItem(self.imageItem)
        self.ui.histogram.fillHistogram(False)  ## for speed
        
        #grid = pg.GridItem()
        #self.view.addItem(grid)
        
        ## Scale bar
        self.scaleBar = pg.ScaleBar(100e-6)
        self.view.addItem(self.scaleBar)

        ### Set up status bar labels
        self.recLabel = QtGui.QLabel()
        self.fpsLabel = pg.ValueLabel(averageTime=2.0, formatStr='{avgValue:.1f} fps')
        self.displayFpsLabel = pg.ValueLabel(averageTime=2.0, formatStr='(displaying {avgValue:.1f} fps')
        self.displayPercentLabel = pg.ValueLabel(averageTime=4.0, formatStr='{avgValue:.1f}%)')
        self.rgnLabel = QtGui.QLabel()
        self.xyLabel = QtGui.QLabel()
        self.tLabel = QtGui.QLabel()
        self.vLabel = QtGui.QLabel()
        
        self.fpsLabel.setFixedWidth(50)
        self.displayFpsLabel.setFixedWidth(100)
        self.displayFpsLabel.setFixedWidth(100)
        self.vLabel.setFixedWidth(50)
        
        #self.logBtn = LogButton('Log')
        self.setStatusBar(StatusBar())
        font = self.xyLabel.font()
        font.setPointSize(8)
        labels = [self.recLabel, self.xyLabel, self.rgnLabel, self.tLabel, self.vLabel, self.displayPercentLabel, self.displayFpsLabel, self.fpsLabel]
        for label in labels:
            label.setFont(font)
            self.statusBar().insertPermanentWidget(0, label)
        
        ## done with UI
        self.show()
        
        ## set up recording thread
        self.recordThread = RecordThread(self, self.module.manager)
        self.recordThread.start()
        self.recordThread.sigShowMessage.connect(self.showMessage)
        self.recordThread.finished.connect(self.recordThreadStopped)
        self.recordThread.sigRecordingFinished.connect(self.recordFinished)
        self.recordThread.sigRecordingFailed.connect(self.recordingFailed)
        

        ## open camera, determine bit depth and sensor area
        self.openCamera()
        
        ## Initialize values
        self.lastCameraPosition = Point(self.camSize[0]*0.5, self.camSize[1]*0.5)
        self.lastCameraScale = Point(1.0, 1.0)
        self.scopeCenter = [self.camSize[0]*0.5, self.camSize[1]*0.5]
        self.cameraScale = [1, 1]
        self.view.setRange(QtCore.QRectF(0, 0, self.camSize[0], self.camSize[1]))
        
        ## Camera region-of-interest control
        self.roi = CamROI(self.camSize, parent=self.cameraItemGroup)
        self.roi.sigRegionChangeFinished.connect(self.regionWidgetChanged)
        self.roi.setZValue(-1)
        self.setRegion()
        
        ## Set up microscope objective borders
        self.borders = []
        #self.cam.sigGlobalTransformChanged.connect(self.cameraMoved)
        
        self.cam.sigGlobalTransformChanged.connect(self.scopeMoved)
        self.scopeMoved()
        self.centerView()
        #scope = self.cam.getScopeDevice()
        #if scope is not None:
            #scope.sigObjectiveListChanged.connect(self.updateBorders)
            ##scope.sigPositionChanged.connect(self.scopeMoved)
            #self.lastCameraPosition = self.cam.getPosition()
            #self.cameraScale = self.cam.getPixelSize()
            #self.scopeCenter = self.cam.getPosition(justScope=True)
            #self.centerView()
        #self.updateBorders()
        
        
        
        ## Initialize values/connections in Camera Dock
        self.setUiBinning(self.binning)
        self.ui.spinExposure.setValue(self.exposure)
        self.ui.spinExposure.setOpts(dec=True, step=1, minStep=100e-6, siPrefix=True, suffix='s', bounds=[0, 10])
        
        ## connect UI signals
        self.ui.btnAcquire.clicked.connect(self.toggleAcquire)
        self.ui.btnRecord.toggled.connect(self.toggleRecord)
        #Signals from self.ui.btnSnap and self.ui.btnRecord are caught by the RecordThread
        self.ui.btnFullFrame.clicked.connect(lambda: self.setRegion())
        #self.ui.scaleToImageBtn.clicked.connect(self.scaleToImage)
        self.proxy1 = SignalProxy(self.ui.binningCombo.currentIndexChanged, slot=self.binningComboChanged)
        self.ui.spinExposure.valueChanged.connect(self.setExposure)  ## note that this signal (from lib.util.SpinBox) is delayed.
        
        ## Signals from Camera device
        self.cam.sigNewFrame.connect(self.newFrame)
        self.cam.sigCameraStopped.connect(self.cameraStopped)
        self.cam.sigCameraStarted.connect(self.cameraStarted)
        self.cam.sigShowMessage.connect(self.showMessage)
        self.ui.graphicsView.scene().sigMouseMoved.connect(self.updateMouse)
        
        ## Connect Background Subtraction Dock
        self.ui.bgBlurSpin.valueChanged.connect(self.updateBackgroundBlur)
        self.ui.collectBgBtn.clicked.connect(self.collectBgClicked)
        self.ui.divideBgBtn.clicked.connect(self.divideClicked)
        self.ui.subtractBgBtn.clicked.connect(self.subtractClicked)
        self.ui.bgBlurSpin.valueChanged.connect(self.requestFrameUpdate)
        
        ## Connect ROI dock
        self.ui.btnAddROI.clicked.connect(self.addROI)
        self.ui.btnClearROIs.clicked.connect(self.clearROIs)
        self.ui.checkEnableROIs.stateChanged.connect(self.enableROIsChanged)
        self.ui.spinROITime.valueChanged.connect(self.setROITime)
        
        ## Connect DisplayGain dock
        self.ui.histogram.sigLookupTableChanged.connect(self.levelsChanged)
        self.ui.histogram.sigLevelsChanged.connect(self.levelsChanged)
        self.ui.btnAutoGain.toggled.connect(self.toggleAutoGain)
        self.ui.btnAutoGain.setChecked(True)
        
        ## Connect Persistent Frames dock
        self.ui.addFrameBtn.clicked.connect(self.addPersistentFrame)
        self.ui.clearFramesBtn.clicked.connect(self.clearPersistentFrames)

        
        ## Check for new frame updates every 16ms
        ## Some checks may be skipped even if there is a new frame waiting to avoid drawing more than 
        ## 60fps.
        self.frameTimer = QtCore.QTimer()
        self.frameTimer.timeout.connect(self.drawFrame)
        self.frameTimer.start(16) ## draw frames no faster than 60Hz
        #QtCore.QTimer.singleShot(1, self.drawFrame)
        ## avoiding possible singleShot-induced crashes


    #@trace
    def openCamera(self, ind=0):
        try:
            self.bitDepth = self.cam.getParam('bitDepth')
            #self.setLevelRange()
            self.camSize = self.cam.getParam('sensorSize')
            self.statusBar().showMessage("Opened camera %s" % self.cam, 5000)
            self.scope = self.module.cam.getScopeDevice()
            
            try:
                bins = self.cam.listParams('binning')[0][0]
            except:
                bins = self.cam.listParams('binningX')[0]
            bins.sort()
            bins.reverse()
            for b in bins:
                self.ui.binningCombo.addItem(str(b))
            
            
        except:
            self.statusBar().showMessage("Error opening camera")
            raise

        
    def scopeMoved(self, p=None):
        ## scope has moved; update viewport and camera outlines.
        ## This is only used when the camera is not running--
        ## if the camera is running, then this is taken care of in drawFrame to
        ## ensure that the image remains stationary on screen.
        if not self.cam.isRunning():
            tr = pg.Transform(self.cam.globalTransform())
            pos = tr.getTranslation()
            diff = pos - self.lastCameraPosition
            self.lastCameraPosition = pos
            scale = tr.getScale()
            if scale == self.lastCameraScale:
                self.view.translateBy(diff) 
            else:  ## if objective has changed, don't translate to follow it.
                self.lastCameraScale = scale
            self.cameraItemGroup.setTransform(tr)
            
    #@trace
    def updateBorders(self):
        """Draw the camera boundaries for each objective"""
        for b in self.borders:
            self.view.removeItem(b)
        self.borders = []
        
        scope = self.module.cam.getScopeDevice()
        if scope is None:
            return
            
        bounds = self.module.cam.getBoundaries()
        for b in bounds:
            border = QtGui.QGraphicsRectItem(QtCore.QRectF(0, 0, 1, 1), self.scopeItemGroup)
            border.scale(b.width(), b.height())
            border.setPos(b.x(), b.y())
            border.setAcceptedMouseButtons(QtCore.Qt.NoButton)
            border.setPen(QtGui.QPen(QtGui.QColor(50,80,80))) 
            border.setZValue(10)
            self.scopeItemGroup.resetTransform()
            self.borders.append(border)
        self.updateCameraDecorations()

    def centerView(self):
        
        #center = self.cam.getPosition(justScope=True)
        #bounds = self.cam.getBoundary().adjusted(center[0], center[1], center[0], center[1])
        bounds = self.cam.getBoundary().boundingRect()
        self.view.setRange(bounds)
        #self.updateCameraDecorations()
        
    #@trace
    def addPersistentFrame(self):
        """Make a copy of the current camera frame and store it in the background"""
        px = self.imageItem.getPixmap()
        if px is None:
            return
        im = QtGui.QGraphicsPixmapItem(px.copy())
        im.setCacheMode(im.NoCache)
        if len(self.persistentFrames) == 0:
            z = -10000
        else:
            z = self.persistentFrames[-1].zValue() + 1
        
        img = self.currentFrame.data()
        info = self.currentFrame.info()
        #s = info['pixelSize']
        #p = info['imagePosition']
        self.persistentFrames.append(im)
        self.addItem(im, z=z)
        im.setTransform(self.currentFrame.globalTransform().as2D())
        
    #@trace
    def addItem(self, item, pos=(0,0), scale=(1,1), z=0):
        """Adds an item into the scene. The image will be automatically scaled and translated when the scope moves."""
        
        self.view.addItem(item)
        
        if pos is None:
            pos = self.lastCameraPosition
        item.setPos(QtCore.QPointF(pos[0], pos[1]))
        item.scale(scale[0], scale[1])
        item.setZValue(z)
    
    def removeItem(self, item):
        self.view.removeItem(item)
    
    #@trace
    def  clearPersistentFrames(self):
        for i in self.persistentFrames:
            self.view.removeItem(i)
        self.persistentFrames = []

    #@trace
    def addROI(self):
        pen = pg.mkPen(pg.intColor(len(self.ROIs)))
        center = self.view.viewRect().center()
        size = [x*50 for x in self.view.viewPixelSize()]
        roi = PlotROI(center, size)
        roi.setZValue(40000)
        roi.setPen(pen)
        self.view.addItem(roi)
        plot = self.ui.plotWidget.plot(pen=pen)
        self.ROIs.append({'roi': roi, 'plot': plot, 'vals': [], 'times': []})
        
    def clearROIs(self):
        for r in self.ROIs:
            self.view.removeItem(r['roi'])
            self.ui.plotWidget.removeItem(r['plot'])
        self.ROIs = []
        
    #@trace
    def clearFrameBuffer(self):
        for r in self.ROIs:
            r['vals'] = []
            r['times'] = []

    #@trace
    def enableROIsChanged(self, b):
        pass
    
    #@trace
    def setROITime(self, val):
        pass

    #@trace
    def toggleRecord(self, b):
        if b:
            self.ui.btnRecord.setChecked(True)
            self.ui.recordXframesCheck.setEnabled(False)
            self.ui.recordXframesSpin.setEnabled(False)
            self.ui.framesLabel.setEnabled(False)
        else:
            self.ui.btnRecord.setChecked(False)
            self.ui.recordXframesCheck.setEnabled(True)
            self.ui.recordXframesSpin.setEnabled(True)
            self.ui.framesLabel.setEnabled(True)
            
    def recordFinished(self):
        self.toggleRecord(False)

    def recordThreadStopped(self):
        self.toggleRecord(False)
        self.ui.btnRecord.setEnabled(False)  ## Recording thread has stopped, can't record anymore.
        self.showMessage("Recording thread died! See console for error message.")
            
    def recordingFailed(self):
        self.toggleRecord(False)
        self.showMessage("Recording failed! See console for error message.")

    #@trace
    def levelsChanged(self):
        if self.ui.btnAutoGain.isChecked() and not self.ignoreLevelChange:
            if self.lastMinMax is None:
                return
            bl, wl = self.getLevels()
            mn, mx = self.lastMinMax
            rng = float(mx-mn)
            if rng == 0:
                return
            newLevels = [(bl-mn) / rng, (wl-mn) / rng]
            #print "autogain:", newLevels
            #import traceback
            #print "\n".join(traceback.format_stack())
            self.autoGainLevels = newLevels
        #self.requestFrameUpdate()

    #@trace
    def requestFrameUpdate(self):
        self.updateFrame = True

    #@trace
    def divideClicked(self):
        self.lastMinMax = None
        self.ui.subtractBgBtn.setChecked(False)
        
    def subtractClicked(self):
        self.lastMinMax = None
        self.ui.divideBgBtn.setChecked(False)
        
    
            
    #@trace
    def showMessage(self, msg):
        self.statusBar().showMessage(str(msg))
        
    def regionWidgetChanged(self, *args):
        self.updateRegion()

        
        
    #@trace
    def updateRegion(self, autoRestart=True):
        self.clearFrameBuffer()
        r = self.roi.parentBounds()
        newRegion = [int(r.left()), int(r.top()), int(r.width()), int(r.height())]
        if self.region != newRegion:
            self.region = newRegion
            self.cam.setParam('region', self.region, autoRestart=autoRestart)
        
    #def scaleToImage(self):
        #self.gv.scaleToImage(self.imageItem)
            
    #@trace
    def closeEvent(self, ev):
        self.quit()

    #@trace
    def quit(self):
        geom = self.geometry()
        uiState = {'window': str(self.saveState().toPercentEncoding()), 'geometry': [geom.x(), geom.y(), geom.width(), geom.height()]}
        Manager.getManager().writeConfigFile(uiState, self.stateFile)
        
        
        
        if self.hasQuit:
            return
        try:
            self.recordThread.sigShowMessage.disconnect(self.showMessage)
            self.recordThread.finished.disconnect(self.recordThreadStopped)
            self.recordThread.sigRecordingFailed.disconnect(self.recordingFailed)
            self.recordThread.sigRecordingFinished.disconnect(self.recordFinished)
        except TypeError:
            pass
        
        try:
            self.cam.sigNewFrame.disconnect(self.newFrame)
            self.cam.sigCameraStopped.disconnect(self.cameraStopped)
            self.cam.sigCameraStarted.disconnect(self.cameraStarted)
            self.cam.sigShowMessage.disconnect(self.showMessage)
        except TypeError:
            pass
        
        self.hasQuit = True
        if self.cam.isRunning():
            self.cam.stop()
            if not self.cam.wait(10000):
                printExc("Timed out while waiting for acq thread exit!")
        if self.recordThread.isRunning():
            self.recordThread.stop()
            if not self.recordThread.wait(10000):
                raise Exception("Timed out while waiting for rec. thread exit!")
        del self.recordThread  ## Required due to cyclic reference
        self.module.quit(fromUi=True)

    #@trace
    def updateMouse(self, pos=None):
        if pos is None:
            if not hasattr(self, 'mouse'):
                return
            pos = self.mouse
        else:
            pos = self.view.mapSceneToView(pos)
        self.mouse = pos
        self.xyLabel.setText("X:%0.1fum Y:%0.1fum" % (pos.x() * 1e6, pos.y() * 1e6))
        
        img = self.imageItem.image
        if img is None:
            return
        pos = self.imageItem.mapFromView(pos)
        if pos.x() < 0 or pos.y() < 0:
            z = ""
        else:
            try:
                z = img[int(pos.x()), int(pos.y())]
                if hasattr(z, 'shape') and len(z.shape) > 0:
                    z = "Z:(%s, %s, %s)" % (str(z[0]), str(z[1]), str(z[2]))
                else:
                    z = "Z:%s" % str(z)
            except IndexError:
                z = ""
    
        
        self.vLabel.setText(z)
            

    #@trace
    def cameraStopped(self):
        self.toggleRecord(False)
        #self.backgroundFrame = None
        self.ui.btnAcquire.setChecked(False)
        self.ui.btnAcquire.setEnabled(True)
        
    #@trace
    def cameraStarted(self):
        #self.AGCLastMax = None
        #self.AGCLastMin = None
        self.ui.btnAcquire.setChecked(True)
        self.ui.btnAcquire.setEnabled(True)

    def binningComboChanged(self, args):
        self.setBinning(*args)
        
    #@trace
    def setBinning(self, ind=None, autoRestart=True):
        """Set camera's binning value. If ind is specified, it is the index from binningCombo from which to grab the new binning value."""
        #self.backgroundFrame = None
        if ind is not None:
            self.binning = int(self.ui.binningCombo.itemText(ind))
        self.cam.setParam('binning', (self.binning, self.binning), autoRestart=autoRestart)
        self.clearFrameBuffer()
        self.updateRgnLabel()
        
    def setUiBinning(self, b):
        ind = self.ui.binningCombo.findText(str(b))
        if ind == -1:
            raise Exception("Binning mode %s not in list." % str(b))
        self.ui.binningCombo.setCurrentIndex(ind)
        
    #@trace
    def setExposure(self, e=None, autoRestart=True):
        if e is not None:
            self.exposure = e
        self.cam.setParam('exposure', self.exposure, autoRestart=autoRestart)
        
    

    #@trace
    def updateCameraDecorations(self):
        ps = self.cameraScale
        pos = self.lastCameraPosition
        cs = self.camSize
        if ps is None:
            return
        
        ## move scope group
        #m = QtGui.QTransform()
        #m.translate(self.scopeCenter[0], self.scopeCenter[1])
        #self.scopeItemGroup.setTransform(m)
        
        ## move and scale camera group
        #m = QtGui.QTransform()
        #m.translate(pos[0], pos[1])
        #m.scale(ps[0], ps[1])
        #m.translate(-cs[0]*0.5, -cs[1]*0.5)
        m = self.cam.globalTransform()
        self.cameraItemGroup.setTransform(pg.Transform(m))
        
        
        
        

    #@trace
    def setRegion(self, rgn=None):
        #self.backgroundFrame = None
        if rgn is None:
            rgn = [0, 0, self.camSize[0]-1, self.camSize[1]-1]
        self.roi.setPos([rgn[0], rgn[1]])
        self.roi.setSize([self.camSize[0], self.camSize[1]])
        self.updateRegion()
            
    #@trace
    def updateRgnLabel(self):
        img = self.imageItem.image
        if img is None:
            return
        self.rgnLabel.setText('[%d, %d, %d, %d] %dx%d' % (self.region[0], self.region[1], (img.shape[0]-1)*self.binning, (img.shape[1]-1)*self.binning, self.binning, self.binning))
    
    #@trace
    #def setLevelRange(self, rmin=None, rmax=None):
        ### 
        #if rmin is None:
            #if self.ui.btnAutoGain.isChecked():
                #rmin = 0.0
                #rmax = 1.0
                #self.ui.histogram.setLevels(rmin, rmax)
            #else:
                #bl, wl = self.getLevels()
                #if self.ui.divideBgBtn.isChecked():
                    #rmin = 0.0
                    #rmax = 2.0
                #else:
                    #rmin = 0.0
                    #rmax = float(2**self.bitDepth - 1)
                    #self.ui.histogram.setLevels(bl/rmax, wl/rmax)
        #self.levelMin = rmin
        #self.levelMax = rmax
        
        
    #@trace
    def getLevels(self):
        return self.ui.histogram.getLevels()

    #@trace
    def toggleAutoGain(self, b):
        if b:
            self.lastAGCMax = None
            self.ui.histogram.vb.setMouseEnabled(x=False, y=False)
            #self.ui.histogram.setLevels(*self.lastMinMax)
        else:
            self.ui.histogram.vb.setMouseEnabled(x=False, y=True)
            

    #@trace
    def toggleAcquire(self):
        if self.ui.btnAcquire.isChecked():
            try:
                self.cam.setParam('triggerMode', 'Normal', autoRestart=False)
                self.setBinning(autoRestart=False)
                self.setExposure(autoRestart=False)
                self.updateRegion(autoRestart=False)
                self.cam.start()
                Manager.logMsg("Camera started aquisition.", importance=0)
            except:
                self.ui.btnAcquire.setChecked(False)
                printExc("Error starting camera:")
                
        else:
            #print "ACQ untoggled, stop record"
            self.toggleRecord(False)
            self.cam.stop()
            Manager.logMsg("Camera stopped acquisition.", importance=0)
            
    #@trace
    def addPlotFrame(self, frame):
        #sys.stdout.write('+')
        prof = Profiler('CameraWindow.addPlotFrame', disabled=True)
        if self.imageItem.width() is None:
            return
        
        ## Get rid of old frames
        minTime = None
        now = ptime.time()
        #if len(self.frameBuffer) > 0:
            #while len(self.frameBuffer) > 0 and self.frameBuffer[0][1]['time'] < (now-self.ui.spinROITime.value()):
                #self.frameBuffer.pop(0)
        for r in self.ROIs:
            #print " >>", r['times'], now, frame[1]['time'], self.ui.spinROITime.value(), now-self.ui.spinROITime.value()
            while len(r['times']) > 0 and r['times'][0] < (now-self.ui.spinROITime.value()):
                r['times'].pop(0)
                r['vals'].pop(0)
            #print " <<", r['times']
            if len(r['times']) > 0 and (minTime is None or r['times'][0] < minTime):
                minTime = r['times'][0]
        if minTime is None:
            minTime = frame.info()['time']
                
        prof.mark('remove old frames')
            
        ## add new frame
        draw = False
        if self.lastPlotTime is None or now - self.lastPlotTime > 0.05:
            draw = True
            self.lastPlotTime = now
            
        for r in self.ROIs:
            d = r['roi'].getArrayRegion(frame.data(), self.imageItem, axes=(0,1))
            prof.mark('get array rgn')
            if d is None:
                continue
            if d.size < 1:
                val = 0
            else:
                val = d.mean()
            r['vals'].append(val)
            r['times'].append(frame.info()['time'])
            prof.mark('append')
            if draw:
                r['plot'].setData(np.array(r['times'])-minTime, r['vals'])
                prof.mark('draw')
        prof.finish()
    
            
    #@trace
    def newFrame(self, frame):
        #if hasattr(self.acquireThread, 'fps') and self.acquireThread.fps is not None:
        #print "    New frame", frame[1]['id']
        lf = None
        if self.nextFrame is not None:
            lf = self.nextFrame
        elif self.currentFrame is not None:
            lf = self.currentFrame
            
        if lf is not None:
            fps = frame.info()['fps']
            if fps is not None:
                #print self.fps, 1.0/dt
                #if self.fps is None:
                    #self.fps = fps
                #else:
                    #self.fps = 1.0 / (0.9/self.fps + 0.1/fps)  ## inversion is necessary because dt varies linearly, but fps varies hyperbolically
                #self.fpsLabel.setText('%02.2ffps' % self.fps)
                self.fpsLabel.setValue(fps)
        
        ## Update ROI plots, if any
        if self.ui.checkEnableROIs.isChecked():
            self.addPlotFrame(frame)
            
        ## self.nextFrame gets picked up by drawFrame() at some point
        if self.nextFrame is not None:
            self.displayPercentLabel.setValue(0.)
        else:
            self.displayPercentLabel.setValue(100.)
            
        self.nextFrame = frame
        
        ## stop collecting bg frames if we are in static mode and time is up
        if self.ui.collectBgBtn.isChecked() and not self.ui.contAvgBgCheck.isChecked():
            #if self.bgStartTime == None:
                #self.bgStartTime = ptime.time()
            timeLeft = self.ui.bgTimeSpin.value() - (ptime.time()-self.bgStartTime)
            if timeLeft > 0:
                self.ui.collectBgBtn.setText("Collecting... (%d)" % int(timeLeft+1))
            else:
                self.ui.collectBgBtn.setChecked(False)
                self.ui.collectBgBtn.setText("Collect Background")
                
        if self.ui.collectBgBtn.isChecked():
            if self.ui.contAvgBgCheck.isChecked():
                x = 1.0 - 1.0 / (self.ui.bgTimeSpin.value()+1.0)
            else:
                x = float(self.bgFrameCount)/(self.bgFrameCount + 1)
                self.bgFrameCount += 1
                
            if self.backgroundFrame == None or self.backgroundFrame.shape != frame.data().shape:
                self.backgroundFrame = frame.data().astype(float)
            else:
                #print "mix:", x
                self.backgroundFrame = x * self.backgroundFrame + (1-x)*frame.data().astype(float)
    
    def collectBgClicked(self, checked):
        ###self.backgroundFrame = ### an average of frames collected -- how to do this?
        if checked:
            if not self.ui.contAvgBgCheck.isChecked():
                self.backgroundFrame = None ## reset background frame
                self.bgFrameCount = 0
                self.bgStartTime = ptime.time()
            self.ui.collectBgBtn.setText("Collecting...")
        else:
            self.ui.collectBgBtn.setText("Collect Background")
        #self.updateBackgroundBlur()
        #pass
    
    def updateBackgroundBlur(self):
        b = self.ui.bgBlurSpin.value()
        if b > 0.0:
            self.blurredBackgroundFrame = scipy.ndimage.gaussian_filter(self.backgroundFrame, (b, b))
        else:
            self.blurredBackgroundFrame = self.backgroundFrame

    def getBackgroundFrame(self):
        if self.backgroundFrame is None:
            return None
        self.updateBackgroundBlur()
        return self.blurredBackgroundFrame
        
    #@trace
    def drawFrame(self):
        if self.hasQuit:
            return
        #sys.stdout.write('+')
        try:
            
            ## If we last drew a frame < 1/30s ago, return.
            t = ptime.time()
            if (self.lastDrawTime is not None) and (t - self.lastDrawTime < .033333):
                #sys.stdout.write('-')
                return
            ## if there is no new frame and no controls have changed, just exit
            if not self.updateFrame and self.nextFrame is None:
                #sys.stdout.write('-')
                return
            self.updateFrame = False
            
            ## If there are no new frames and no previous frames, then there is nothing to draw.
            if self.currentFrame is None and self.nextFrame is None:
                #sys.stdout.write('-')
                return

            prof = debug.Profiler('CameraWindow.drawFrame', disabled=True)
            prof.mark() 
            ## We will now draw a new frame (even if the frame is unchanged)
            if self.lastDrawTime is not None:
                fps = 1.0 / (t - self.lastDrawTime)
                #if self.displayFps is None:
                    #self.displayFps = fps
                #else:
                    #self.fps = 1.0 / (0.9/self.displayFps + 0.1/fps)  ## inversion is necessary because dt varies linearly, but fps varies hyperbolically
                #self.displayFpsLabel.setText('(displaying %02.2ffps)' % self.displayFps)
                self.displayFpsLabel.setValue(fps)
            self.lastDrawTime = t
            prof.mark() 
            
            ## Handle the next available frame, if there is one.
            if self.nextFrame is not None:
                self.currentFrame = self.nextFrame
                self.nextFrame = None
                #(data, info) = self.currentFrame
                #self.currentClipMask = (data >= (2**self.bitDepth * 0.99)) ##mask of pixels that are saturated
                
                ## If continous background division is enabled, mix the current frame into the background frame
                #if self.ui.continuousBgBtn.isChecked():
                    #if self.backgroundFrame is None or self.backgroundFrame.shape != data.shape:
                        #self.backgroundFrame = data.astype(float)
                    #s = 1.0 - 1.0 / (self.ui.bgTimeSpin.value()+1.0)
                    #self.backgroundFrame *= s
                    #self.backgroundFrame += data * (1.0-s)
                #if self.ui.continuousBgBtn.isChecked() or self.ui.staticBgBtn.isChecked():
                #if self.ui.divideBgBtn.isChecked():
                    #self.updateBackgroundBlur()
            data = self.currentFrame.data()
            info = self.currentFrame.info()
            prof.mark() 

            
            ## divide the background out of the current frame if needed
            if self.ui.divideBgBtn.isChecked():
                bg = self.getBackgroundFrame()
                if bg is not None and bg.shape == data.shape:
                    data = data / bg
            elif self.ui.subtractBgBtn.isChecked():
                bg = self.getBackgroundFrame()
                if bg is not None and bg.shape == data.shape:
                    data = data - bg
            prof.mark() 
            
            ## Set new levels if auto gain is enabled
            if self.ui.btnAutoGain.isChecked():
                cw = self.ui.spinAutoGainCenterWeight.value()
                (w,h) = data.shape
                center = data[w/2.-w/6.:w/2.+w/6., h/2.-h/6.:h/2.+h/6.]
                minVal = data.min() * (1.0-cw) + center.min() * cw
                maxVal = data.max() * (1.0-cw) + center.max() * cw
                
                ## Smooth min/max range to avoid noise
                if self.lastMinMax is None:
                    minVal = minVal
                    maxVal = maxVal
                else:
                    s = 1.0 - 1.0 / (self.ui.spinAutoGainSpeed.value()+1.0)
                    minVal = self.lastMinMax[0] * s + minVal * (1.0-s)
                    maxVal = self.lastMinMax[1] * s + maxVal * (1.0-s)
                    
                self.lastMinMax = [minVal, maxVal]
                
                ## and convert fraction of previous range into new levels
                bl = self.autoGainLevels[0] * (maxVal-minVal) + minVal
                wl = self.autoGainLevels[1] * (maxVal-minVal) + minVal
                
                self.ignoreLevelChange = True
                try:
                    self.ui.histogram.setLevels(bl, wl)
                    self.ui.histogram.setHistogramRange(minVal, maxVal, padding=0.05)
                finally:
                    self.ignoreLevelChange = False
            prof.mark() 
            
            ## Update histogram plot
            #self.updateHistogram(self.currentFrame[0], wl, bl)
            
            ## Translate and scale image based on ROI and binning
            #m = QtGui.QTransform()
            #m.translate(info['region'][0], info['region'][1])
            #m.scale(*info['binning'])
            prof.mark() 
            
            ## update image in viewport
            self.imageItem.updateImage(data)#, levels=[bl, wl])
            self.imageItem.setTransform(self.currentFrame.frameTransform().as2D())
            prof.mark() 

            ## Update viewport to correct for scope movement/scaling
            ## TODO: fix these
            tr = pg.Transform(self.currentFrame.cameraTransform())
            newPos = tr.getTranslation()
            diff = newPos - self.lastCameraPosition
            self.view.translateBy(diff)
            self.lastCameraPosition = newPos
            
            newScale = tr.getScale()
            if newScale != self.lastCameraScale:
                self.centerView()
            self.lastCameraScale = newScale
            
            #if tr.pos() != self.lastCameraPosition:
                #self.sigCameraPosChanged.emit()
                #diff = newPos - self.lastCameraPosition
                #self.view.translateBy(diff)
                #self.lastCameraPosition = newPos
                #self.scopeCenter = info['scopePosition']
                #self.updateCameraDecorations()
            #prof.mark()
            
            
            #newScale = [info['pixelSize'][0] / info['binning'][0], info['pixelSize'][1] / info['binning'][1]]
            #if newScale != self.cameraScale:  ## If scale has changed, re-center on new objective.
                #self.sigCameraScaleChanged.emit()
                #self.centerView()
                #self.cameraScale = newScale
                #self.updateCameraDecorations()
            #prof.mark() 

            ## move and scale image item group  - sets image to correct position/scale based on scope position and objective
            #m = QtGui.QTransform()
            #m.translate(*self.lastCameraPosition)
            #m.scale(*self.cameraScale)
            #m.translate(-self.camSize[0]*0.5, -self.camSize[1]*0.5)
            self.cameraItemGroup.setTransform(tr)
            self.imageItemGroup.setTransform(tr)
            prof.mark() 

            ## update info for pixel under mouse pointer
            self.updateMouse()
            self.updateRgnLabel()
            
            prof.mark() 
            prof.finish()
            #if self.ui.checkEnableROIs.isChecked():
                #self.ui.plotWidget.replot()
           


        except:
            printExc('Error while drawing new frames:')
        finally:
            pass
            #QtCore.QTimer.singleShot(1, self.drawFrame)
            ## avoiding possible singleShot-induced crashes

        #sys.stdout.write('!')

    #def updateHistogram(self, data, wl, bl):
        #return
        ##now = time.time()
        ##if now > self.lastHistogramUpdate + 1.0:
            ##avg = data.mean()
            ##self.avgLevelLine.setLine(0.0, avg, 1.0, avg)
            ##bins = np.linspace(0, 2**self.bitDepth, 500)
            ##h = np.histogram(data, bins=bins)
            ##xVals = h[0].astype(np.float32)/h[0].max()
            ##self.histogramCurve.setData(x=xVals, y=bins[:-1])
            ##self.lastHistogramUpdate = now


class CameraInterface(QtCore.QObject):
    """
    This class provides all the functionality necessary for a camera to display images and controls within the camera module's main window. Each camera that connects to the window must implement an instance of this interface.
    """
    def __init__(self):
        QtCore.QObject.__init__(self)
        
        
    
    
    