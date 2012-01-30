# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './ui/SpeedLimitDialog.ui'
#
# Created: Tue Jan  3 14:09:20 2012
#      by: pyside-uic 0.2.11 running on PySide 1.0.9
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(194, 93)
        Dialog.setModal(True)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setHorizontalSpacing(10)
        self.formLayout.setObjectName("formLayout")
        self.speedLimitLabel = QtGui.QLabel(Dialog)
        self.speedLimitLabel.setObjectName("speedLimitLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.speedLimitLabel)
        self.speedLimitSpinBox = QtGui.QSpinBox(Dialog)
        self.speedLimitSpinBox.setObjectName("speedLimitSpinBox")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.speedLimitSpinBox)
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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Speed Limit", None, QtGui.QApplication.UnicodeUTF8))
        self.speedLimitLabel.setText(QtGui.QApplication.translate("Dialog", "Speed Limit", None, QtGui.QApplication.UnicodeUTF8))
        self.speedLimitSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", " km/h", None, QtGui.QApplication.UnicodeUTF8))

