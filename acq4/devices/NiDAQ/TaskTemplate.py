# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './acq4/devices/NiDAQ/TaskTemplate.ui'
#
# Created: Tue Dec 24 01:49:08 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(200, 296)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.triggerDevList = QtGui.QComboBox(Form)
        self.triggerDevList.setObjectName(_fromUtf8("triggerDevList"))
        self.triggerDevList.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.triggerDevList, 1, 1, 1, 2)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.numPtsLabel = QtGui.QLabel(Form)
        self.numPtsLabel.setObjectName(_fromUtf8("numPtsLabel"))
        self.gridLayout.addWidget(self.numPtsLabel, 0, 1, 1, 1)
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_3.setMargin(0)
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_7 = QtGui.QLabel(self.groupBox)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_3.addWidget(self.label_7, 0, 0, 1, 1)
        self.denoiseCombo = QtGui.QComboBox(self.groupBox)
        self.denoiseCombo.setObjectName(_fromUtf8("denoiseCombo"))
        self.denoiseCombo.addItem(_fromUtf8(""))
        self.denoiseCombo.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.denoiseCombo, 0, 1, 1, 1)
        self.denoiseStack = QtGui.QStackedWidget(self.groupBox)
        self.denoiseStack.setObjectName(_fromUtf8("denoiseStack"))
        self.page_4 = QtGui.QWidget()
        self.page_4.setObjectName(_fromUtf8("page_4"))
        self.denoiseStack.addWidget(self.page_4)
        self.page_3 = QtGui.QWidget()
        self.page_3.setObjectName(_fromUtf8("page_3"))
        self.gridLayout_7 = QtGui.QGridLayout(self.page_3)
        self.gridLayout_7.setMargin(0)
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.label_13 = QtGui.QLabel(self.page_3)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.gridLayout_7.addWidget(self.label_13, 0, 0, 1, 1)
        self.denoiseThresholdSpin = QtGui.QDoubleSpinBox(self.page_3)
        self.denoiseThresholdSpin.setProperty("value", 4.0)
        self.denoiseThresholdSpin.setObjectName(_fromUtf8("denoiseThresholdSpin"))
        self.gridLayout_7.addWidget(self.denoiseThresholdSpin, 0, 1, 1, 1)
        self.label_16 = QtGui.QLabel(self.page_3)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_7.addWidget(self.label_16, 1, 0, 1, 1)
        self.denoiseWidthSpin = QtGui.QSpinBox(self.page_3)
        self.denoiseWidthSpin.setMinimum(1)
        self.denoiseWidthSpin.setMaximum(100000)
        self.denoiseWidthSpin.setProperty("value", 1)
        self.denoiseWidthSpin.setObjectName(_fromUtf8("denoiseWidthSpin"))
        self.gridLayout_7.addWidget(self.denoiseWidthSpin, 1, 1, 1, 1)
        self.denoiseStack.addWidget(self.page_3)
        self.gridLayout_3.addWidget(self.denoiseStack, 1, 1, 1, 1)
        self.label_9 = QtGui.QLabel(self.groupBox)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout_3.addWidget(self.label_9, 2, 0, 1, 1)
        self.filterCombo = QtGui.QComboBox(self.groupBox)
        self.filterCombo.setObjectName(_fromUtf8("filterCombo"))
        self.filterCombo.addItem(_fromUtf8(""))
        self.filterCombo.addItem(_fromUtf8(""))
        self.filterCombo.addItem(_fromUtf8(""))
        self.gridLayout_3.addWidget(self.filterCombo, 2, 1, 1, 1)
        self.filterStack = QtGui.QStackedWidget(self.groupBox)
        self.filterStack.setObjectName(_fromUtf8("filterStack"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.gridLayout_6 = QtGui.QGridLayout(self.page)
        self.gridLayout_6.setMargin(0)
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.filterStack.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.gridLayout_5 = QtGui.QGridLayout(self.page_2)
        self.gridLayout_5.setMargin(0)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label_11 = QtGui.QLabel(self.page_2)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.gridLayout_5.addWidget(self.label_11, 0, 0, 1, 1)
        self.besselCutoffSpin = SpinBox(self.page_2)
        self.besselCutoffSpin.setProperty("value", 2.0)
        self.besselCutoffSpin.setObjectName(_fromUtf8("besselCutoffSpin"))
        self.gridLayout_5.addWidget(self.besselCutoffSpin, 0, 1, 1, 1)
        self.label_12 = QtGui.QLabel(self.page_2)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.gridLayout_5.addWidget(self.label_12, 1, 0, 1, 1)
        self.besselOrderSpin = QtGui.QSpinBox(self.page_2)
        self.besselOrderSpin.setMinimum(1)
        self.besselOrderSpin.setMaximum(16)
        self.besselOrderSpin.setProperty("value", 4)
        self.besselOrderSpin.setObjectName(_fromUtf8("besselOrderSpin"))
        self.gridLayout_5.addWidget(self.besselOrderSpin, 1, 1, 1, 1)
        self.filterStack.addWidget(self.page_2)
        self.page_5 = QtGui.QWidget()
        self.page_5.setObjectName(_fromUtf8("page_5"))
        self.gridLayout_4 = QtGui.QGridLayout(self.page_5)
        self.gridLayout_4.setMargin(0)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.label_14 = QtGui.QLabel(self.page_5)
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.gridLayout_4.addWidget(self.label_14, 0, 1, 1, 1)
        self.label_15 = QtGui.QLabel(self.page_5)
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.gridLayout_4.addWidget(self.label_15, 0, 2, 1, 2)
        self.label_5 = QtGui.QLabel(self.page_5)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_4.addWidget(self.label_5, 1, 0, 1, 1)
        self.butterworthPassbandSpin = SpinBox(self.page_5)
        self.butterworthPassbandSpin.setProperty("value", 1.0)
        self.butterworthPassbandSpin.setObjectName(_fromUtf8("butterworthPassbandSpin"))
        self.gridLayout_4.addWidget(self.butterworthPassbandSpin, 1, 1, 1, 1)
        self.butterworthPassDBSpin = QtGui.QDoubleSpinBox(self.page_5)
        self.butterworthPassDBSpin.setProperty("value", 2.0)
        self.butterworthPassDBSpin.setObjectName(_fromUtf8("butterworthPassDBSpin"))
        self.gridLayout_4.addWidget(self.butterworthPassDBSpin, 1, 2, 1, 2)
        self.label_6 = QtGui.QLabel(self.page_5)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_4.addWidget(self.label_6, 2, 0, 1, 1)
        self.butterworthStopbandSpin = SpinBox(self.page_5)
        self.butterworthStopbandSpin.setProperty("value", 2.0)
        self.butterworthStopbandSpin.setObjectName(_fromUtf8("butterworthStopbandSpin"))
        self.gridLayout_4.addWidget(self.butterworthStopbandSpin, 2, 1, 1, 1)
        self.butterworthStopDBSpin = QtGui.QDoubleSpinBox(self.page_5)
        self.butterworthStopDBSpin.setProperty("value", 10.0)
        self.butterworthStopDBSpin.setObjectName(_fromUtf8("butterworthStopDBSpin"))
        self.gridLayout_4.addWidget(self.butterworthStopDBSpin, 2, 2, 1, 2)
        self.filterStack.addWidget(self.page_5)
        self.gridLayout_3.addWidget(self.filterStack, 3, 1, 1, 1)
        self.label_8 = QtGui.QLabel(self.groupBox)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_3.addWidget(self.label_8, 4, 0, 1, 1)
        self.downsampleSpin = QtGui.QSpinBox(self.groupBox)
        self.downsampleSpin.setMinimum(1)
        self.downsampleSpin.setMaximum(10000000)
        self.downsampleSpin.setProperty("value", 1)
        self.downsampleSpin.setObjectName(_fromUtf8("downsampleSpin"))
        self.gridLayout_3.addWidget(self.downsampleSpin, 4, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 3, 0, 1, 3)
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.rateSpin = SpinBox(self.groupBox_2)
        self.rateSpin.setMinimum(0.01)
        self.rateSpin.setMaximum(1000000.0)
        self.rateSpin.setProperty("value", 40000.0)
        self.rateSpin.setObjectName(_fromUtf8("rateSpin"))
        self.gridLayout_2.addWidget(self.rateSpin, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.groupBox_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.periodSpin = SpinBox(self.groupBox_2)
        self.periodSpin.setMinimum(1.0)
        self.periodSpin.setMaximum(10000.0)
        self.periodSpin.setProperty("value", 1.0)
        self.periodSpin.setObjectName(_fromUtf8("periodSpin"))
        self.gridLayout_2.addWidget(self.periodSpin, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 3)

        self.retranslateUi(Form)
        self.denoiseStack.setCurrentIndex(0)
        self.filterStack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_2.setText(_translate("Form", "Trigger", None))
        self.triggerDevList.setItemText(0, _translate("Form", "No Trigger", None))
        self.label_3.setText(_translate("Form", "Points", None))
        self.numPtsLabel.setText(_translate("Form", "0", None))
        self.groupBox.setTitle(_translate("Form", "Post-processing", None))
        self.label_7.setText(_translate("Form", "Denoise", None))
        self.denoiseCombo.setToolTip(_translate("Form", "Denoise method to use.\n"
"- Pointwise method compares each point to its neighbors", None))
        self.denoiseCombo.setItemText(0, _translate("Form", "None", None))
        self.denoiseCombo.setItemText(1, _translate("Form", "Pointwise", None))
        self.label_13.setText(_translate("Form", "Threshold", None))
        self.denoiseThresholdSpin.setToolTip(_translate("Form", "Minimum threshold of detected noise events", None))
        self.label_16.setText(_translate("Form", "Width", None))
        self.denoiseWidthSpin.setToolTip(_translate("Form", "Maximum radius of detected noise events", None))
        self.label_9.setText(_translate("Form", "Filter", None))
        self.filterCombo.setToolTip(_translate("Form", "Lowpass filter types to use for AI channels. Filter is applied before downsampling.", None))
        self.filterCombo.setItemText(0, _translate("Form", "None", None))
        self.filterCombo.setItemText(1, _translate("Form", "Bessel", None))
        self.filterCombo.setItemText(2, _translate("Form", "Butterworth", None))
        self.label_11.setText(_translate("Form", "Cutoff", None))
        self.label_12.setText(_translate("Form", "Order", None))
        self.label_14.setText(_translate("Form", "Freq.", None))
        self.label_15.setText(_translate("Form", "dB", None))
        self.label_5.setText(_translate("Form", "pass", None))
        self.butterworthPassbandSpin.setToolTip(_translate("Form", "Upper frequency of butterworth passband in multiples of maximum nyquist frequency (sample rate / 2).", None))
        self.butterworthPassDBSpin.setToolTip(_translate("Form", "Maximum amplitude of loss in passband", None))
        self.label_6.setText(_translate("Form", "stop", None))
        self.butterworthStopbandSpin.setToolTip(_translate("Form", "Lower frequency of butterworth stopband in multiples of maximum nyquist frequency (sample rate / 2).", None))
        self.butterworthStopDBSpin.setToolTip(_translate("Form", "Minimum amplitude of loss in stopband", None))
        self.label_8.setText(_translate("Form", "Downsample", None))
        self.downsampleSpin.setToolTip(_translate("Form", "Amount DAQ data should be downsampled before returning results (output data is not downsampled before sending to the DAQ). DI/DO data is downsampled by subsampling, AI/AO data is downsampled by averaging. ", None))
        self.downsampleSpin.setSuffix(_translate("Form", "x", None))
        self.groupBox_2.setTitle(_translate("Form", "Timing", None))
        self.label.setText(_translate("Form", "Rate", None))
        self.rateSpin.setSuffix(_translate("Form", " Hz", None))
        self.label_4.setText(_translate("Form", "Period", None))
        self.periodSpin.setSuffix(_translate("Form", " μs", None))

from acq4.pyqtgraph import SpinBox
