import os
from PyQt5 import uic
from PyQt5 import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'CamadaBuffer_dialog_base.ui'))

class CamadaBufferDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(CamadaBufferDialog, self).__init__(parent)
        
        self.setupUi(self)
