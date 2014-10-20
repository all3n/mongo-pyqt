#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
'''
Created on 2014年9月20日

@author: wanghch

'''
import sys
import logging
from PyQt5.Qt import QStandardItem,QTreeWidgetItem, QMenu, QAction
import pymongo
from utils.MongoUtils import MongoUtils
import json
import traceback
from PyQt5 import QtGui
import math
import time
import re

'''
@property  mainWindow:MainWindow
'''
class AppController(object):
    '''
    classdocs
    '''


    
    
    
    def onContextMenu(self):
        print self.curDb+"."+self.curCol
        self.page = 1
        self.queryjson = {}
        self.findRecord(self.curDb,self.curCol,self.queryjson,self.page,self.limit)
    
    
    def __init__(self,app):
        '''
        Constructor
        '''
        self.app = app
        self.setModel(self.app.mongoResultModel)
        self.setView(self.app.ui_MainWindow)
        self.mgutils = MongoUtils()
        
        self.log = logging.getLogger("AppController")
        
        self.limit = 20
        
        self.ctxAction = QAction("Find",self.mainWindow.treeWidget)
        self.ctxAction.triggered.connect(self.onContextMenu)
        
    def connectServer(self):
#         self.mongoResultModel.setColumnCount(3)
#         self.mongoResultModel.setRowCount(5)
#         self.mongoResultModel.setItem(1, 1, QStandardItem("afsdf"))
        host = self.mainWindow.mongoHost.text()
        try:
            self.conn = pymongo.Connection(host,27017)
            self.showMsg("connect "+host+" success!")
            self.databases = self.conn.database_names()
            
                
                
            colsMap = {}
            for db in self.databases:
                colsMap[db] = self.conn[db].collection_names()
                
            self.mainWindow.treeWidget.clear()
            treeItems = []
            for db in self.databases:
                dbItem = QTreeWidgetItem(self.mainWindow.treeWidget,[db])
                treeItems.append(dbItem)
                cols = colsMap[db]
                for col in cols:
                    colItem = QTreeWidgetItem(dbItem,[col])
                    
                
            self.mainWindow.treeWidget.insertTopLevelItems(0,treeItems)
            
            
        except Exception,e:
            self.log.error(e)
            self.showMsg(e.message)
            traceback.print_exc(file=sys.stdout)
            
        self.log.info(self.databases)
        pass
    
    
    def query(self):
        self.mongoResultModel.clear()
        query = self.mainWindow.query.text()
        query = re.sub(r"(,?)(\w+?)\s*?:", r"\1'\2':", query).replace("'", "\"")
       
         
        treeItem = self.mainWindow.treeWidget.currentItem()
        dbTreeItem = treeItem.parent()
        
        self.page = 1
        
        print treeItem,dbTreeItem
        if dbTreeItem == None:
            self.showMsg("please select a collection")
            return
        
        collName = treeItem.text(0)
        dbName = dbTreeItem.text(0)
         
        self.curCol = collName
        self.curDb = dbName
    

        limit = self.limit
        
        
        try:
            if(query == ""):
                queryjson = {}
            else:
                queryjson = json.loads(query)
            
            
            self.queryjson = queryjson
            self.findRecord(dbName,collName,queryjson,self.page,limit)
            
        except Exception,e:
            self.log.error(e)
            self.showMsg(e.message)
            traceback.print_exc(file=sys.stdout)
        #db = self.conn[selectDb]
    
    
    def findRecord(self, dbName, collName,queryjson,page,limit):
        
        preview = self.mgutils.preview(collName,queryjson,page,limit)
        self.mainWindow.preview.setText(preview)
        
        self.mainWindow.prevBtn.setEnabled(page > 1)
        
        
        
        db = self.conn[dbName]
        coll = db[collName]
        
       
        
        
        skipnum = (page - 1) * limit
        
        self.start = time.time()
        cursor = coll.find(queryjson).limit(limit).skip(skipnum)
        
        
        totalCounts = cursor.count()
        pages = int(math.ceil(totalCounts/float(limit)));
        self.mainWindow.nextBtn.setEnabled(page < pages)
        
        self.mainWindow.paginationinfo.setText(str(self.page)+"/"+str(pages) + " total:"+str(totalCounts))
         
        self.fillTable(cursor)
    
    
    def fillTable(self,cursor):
        i = 0
        setheader = False
        labels = None
        for item in cursor:
            j = 0
            items = item.items()
            
            if setheader == False:
                self.mongoResultModel.setColumnCount(len(items))
                labels = item.keys()
                labels.sort()
                self.mongoResultModel.setHorizontalHeaderLabels(labels)
                setheader = True
            
            
            for (field,value) in items:
                try:
                    fieldindex = labels.index(field)
                except ValueError:
                    labels.append(field)
                    fieldindex = len(labels) - 1
                    self.mongoResultModel.setHorizontalHeaderLabels(labels)
            
                self.mongoResultModel.setItem(i, fieldindex, QStandardItem(str(value).encode("UTF-8")))
                j += 1
            i += 1
          
        self.end = time.time()
        self.mainWindow.querytime.setText("query use:"+str('%.4f' % (self.end-self.start))+" s") 
    
    def setView(self,mainWindow):
        self.mainWindow = mainWindow
        
        
    
    def setModel(self,model):
        self.mongoResultModel = model
        
    def clickTable(self):
        index = self.mainWindow.tableview.currentIndex()
#         self.log.debug(str(index.row())+","+str(index.column())+" clicked")
        selectClickValue = self.mongoResultModel.data(index)
        self.mainWindow.viewDetailLabel.setText(selectClickValue)
        
        
        
    def showTreeMenu(self,point):
        item = self.mainWindow.treeWidget.itemAt(point)
        if item != None and item.parent() != None:
            self.curDb = item.parent().text(0)
            self.curCol = item.text(0)
            ctxMenu = QMenu()
            ctxMenu.addAction(self.ctxAction)
            ctxMenu.exec_(QtGui.QCursor.pos())
        
        
        
    def showMsg(self,msg):
        self.app.mainWindow.statusBar().showMessage(msg)
        
        
    def prevPagination(self):
        self.page -= 1
        self.pagination()
        
    def nextPagination(self): 
        self.page += 1
        self.pagination()
    
    def pagination(self):
        self.findRecord(self.curDb, self.curCol, self.queryjson, self.page, self.limit)