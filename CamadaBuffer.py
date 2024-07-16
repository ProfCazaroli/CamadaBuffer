from PyQt5.QtCore import QSettings, QTranslator, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QFileDialog
from .resources import *
from .CamadaBuffer_dialog import CamadaBufferDialog
import os.path
from qgis.core import *
import sys, os
from osgeo import ogr
import processing

class CamadaBuffer:
    def __init__(self, iface):
        self.iface = iface
        
        self.plugin_dir = os.path.dirname(__file__)
        
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CamadaBuffer{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []  # Declare instance attributes
        self.menu = self.tr(u'&Buffer em Camada') # Nome da Rotina no Menu

        self.first_start = None

    def tr(self, message):
        return QCoreApplication.translate('CamadaBuffer', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/CamadaBuffer/icon.png' # Ícone da chamada do Plugin
        # nome da Rotina
        self.add_action(
            icon_path,
            text=self.tr(u'Coloca Buffer em Camada'), 
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&CamadaBuffer'),
                action)
            self.iface.removeToolBarIcon(action)

    #=======================Elementos da Tela criada no Qt Designer==================================
    def comboBoxCamadas(self): # ComboBox de Camadas do Projeto
        self.dlg.cmbCamadas.clear() 
        camadasProj = [c for c in QgsProject.instance().mapLayers().values()]

        listaCamadas = []
        for c in camadasProj:
            if c.type() == QgsMapLayer.VectorLayer:
                listaCamadas.append(c.name())

        self.dlg.cmbCamadas.addItems(listaCamadas)

    def carregaCamada(self): # caso queira carregar uma camada que não está no Projeto
        c = str(QFileDialog.getOpenFileName(caption="Escolha a Camada", filter="ShapeFiles (*.shp)")[0])
        if c != "":
            self.iface.addVectorLayer(c, str.split(os.path.basename(c),".")[0],"ogr")
            self.comboBoxCamadas()

    def camadaEntrada(self): # a camada escolhida no comboBox
        camadaEnt = None
        camadaEnt = self.dlg.cmbCamadas.currentText()

        return camadaEnt

    def camadaSaida(self): # escolhendo a camada para gravar
        c = str(QFileDialog.getSaveFileName(caption="Escolha a Camada de Saída", filter="ShapeFiles (*.shp)")[0])
        self.dlg.txtCamada.setText(c) # coloca o nome da camada no QLineEdit

    def variaveis(self): # variáveis que serão usadas na função run
        self.camada = self.camadaEntrada()
        self.camadaSaida = self.dlg.txtCamada.text()
        self.faixa = self.dlg.valBuffer.value()

    #===============================================================================

    def run(self): #XXX onde o Plugin é excutado
        if self.first_start == True:
            self.first_start = False
            self.dlg = CamadaBufferDialog()

        self.dlg.show()
        
        #Carrega os elementos da Tela
        self.selecionaCamada()
        self.dlg.cmdCamadaEnt.clicked.connect(self.carregaCamada) # definido no name lá no Qt Designer
        self.dlg.cmdCamadaSai.clicked.connect(self.carregaCamada)

        result = self.dlg.exec_()
        
        if result: 
            self.variaveis() # carrega as variáveis para serem utilizadas

            # começa o algoritmo da funcionalidade do Plugin
            buffer = processing.run("native:buffer", {'INPUT': self.camada,
            'DISTANCE': self.faixa,
            'DISSOLVE': False,
            'END_CAP _STYLE': 0,
            'JOIN_STYLE': 0,
            'OUTPUT': self.saida})

            self.iface.addVectorLayer(self.saida, str.split(os.path.basename(self.saida),".")[0], "ogr")
            pass
