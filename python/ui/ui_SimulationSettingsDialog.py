# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/SimulationSettingsDialog.ui'
#
# Created: Tue Jan  3 14:09:20 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(317, 175)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setObjectName("formLayout")
        self.initialNumberOfVehiclesLabel = QtGui.QLabel(Dialog)
        self.initialNumberOfVehiclesLabel.setObjectName("initialNumberOfVehiclesLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.initialNumberOfVehiclesLabel)
        self.initialNumberOfVehiclesSpinBox = QtGui.QSpinBox(Dialog)
        self.initialNumberOfVehiclesSpinBox.setMinimum(0)
        self.initialNumberOfVehiclesSpinBox.setMaximum(10000)
        self.initialNumberOfVehiclesSpinBox.setProperty("value", 100)
        self.initialNumberOfVehiclesSpinBox.setObjectName("initialNumberOfVehiclesSpinBox")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.initialNumberOfVehiclesSpinBox)
        self.minVehicleSpeedLabel = QtGui.QLabel(Dialog)
        self.minVehicleSpeedLabel.setObjectName("minVehicleSpeedLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.minVehicleSpeedLabel)
        self.minVehicleSpeedSpinBox = QtGui.QSpinBox(Dialog)
        self.minVehicleSpeedSpinBox.setMinimum(20)
        self.minVehicleSpeedSpinBox.setMaximum(200)
        self.minVehicleSpeedSpinBox.setSingleStep(10)
        self.minVehicleSpeedSpinBox.setProperty("value", 40)
        self.minVehicleSpeedSpinBox.setObjectName("minVehicleSpeedSpinBox")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.minVehicleSpeedSpinBox)
        self.maxVehicleSpeedLabel = QtGui.QLabel(Dialog)
        self.maxVehicleSpeedLabel.setObjectName("maxVehicleSpeedLabel")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.maxVehicleSpeedLabel)
        self.maxVehicleSpeedSpinBox = QtGui.QSpinBox(Dialog)
        self.maxVehicleSpeedSpinBox.setMinimum(20)
        self.maxVehicleSpeedSpinBox.setMaximum(200)
        self.maxVehicleSpeedSpinBox.setProperty("value", 160)
        self.maxVehicleSpeedSpinBox.setObjectName("maxVehicleSpeedSpinBox")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.maxVehicleSpeedSpinBox)
        self.trafficLightsStrategyLabel = QtGui.QLabel(Dialog)
        self.trafficLightsStrategyLabel.setObjectName("trafficLightsStrategyLabel")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.trafficLightsStrategyLabel)
        self.trafficLightsStrategyComboBox = QtGui.QComboBox(Dialog)
        self.trafficLightsStrategyComboBox.setEditable(False)
        self.trafficLightsStrategyComboBox.setObjectName("trafficLightsStrategyComboBox")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.trafficLightsStrategyComboBox)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Simulation Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.initialNumberOfVehiclesLabel.setText(QtGui.QApplication.translate("Dialog", "Initial Number of Vehicles", None, QtGui.QApplication.UnicodeUTF8))
        self.minVehicleSpeedLabel.setText(QtGui.QApplication.translate("Dialog", "Minimum Vehicle Speed", None, QtGui.QApplication.UnicodeUTF8))
        self.minVehicleSpeedSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", " km/h", None, QtGui.QApplication.UnicodeUTF8))
        self.maxVehicleSpeedLabel.setText(QtGui.QApplication.translate("Dialog", "Maximum Vehicle Speed", None, QtGui.QApplication.UnicodeUTF8))
        self.maxVehicleSpeedSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", " km/h", None, QtGui.QApplication.UnicodeUTF8))
        self.trafficLightsStrategyLabel.setText(QtGui.QApplication.translate("Dialog", "Traffic Lights Strategy", None, QtGui.QApplication.UnicodeUTF8))

