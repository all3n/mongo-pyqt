#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
'''
Created on 2014年9月20日

@author: wanghch
'''
import logging.config

from PyQt5.Qt import QApplication, QStandardItem, QMainWindow, QTableView
import sys
from model.MongoResultModel import MongoResultModel
from PyQt5 import Qt, QtCore
from controller.AppController import AppController
from view.MainWindow import Ui_MainWindow


class Application(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        logging.config.fileConfig("logging.conf")
        self.log = logging.getLogger("Application")
        
        
        
    def setupModels(self):
        self.mongoResultModel = MongoResultModel()
        pass
    
    
    def setupSlot(self):
        self.ui_MainWindow.tableview.setModel(self.mongoResultModel)
        self.ui_MainWindow.connectBtn.clicked.connect(self.appctl.connectServer)
        self.ui_MainWindow.querybtn.clicked.connect(self.appctl.query)
        self.ui_MainWindow.tableview.clicked.connect(self.appctl.clickTable)
        self.ui_MainWindow.treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui_MainWindow.treeWidget.customContextMenuRequested.connect(self.appctl.showTreeMenu)
        
        self.ui_MainWindow.prevBtn.clicked.connect(self.appctl.prevPagination)
        self.ui_MainWindow.nextBtn.clicked.connect(self.appctl.nextPagination)
        
    
    
    def setupCtl(self):
        self.appctl = AppController(self)

    
    def run(self):
        self.log.info("app is start")
        
        self.qtapp = QApplication(sys.argv)
        
        self.setupUi()
        self.setupModels()
        self.setupCtl()
        self.setupSlot()
        
        self.ui_MainWindow.mongoHost.setText("10.19.0.240")
        
        sys.exit(self.qtapp.exec_())
        
    def setupUi(self):
        self.mainWindow = QMainWindow()
        self.ui_MainWindow = Ui_MainWindow()
        self.ui_MainWindow.setupUi(self.mainWindow)
        self.mainWindow.show()
        pass