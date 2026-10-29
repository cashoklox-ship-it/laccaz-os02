#!/usr/bin/python3
import json, os, shlex, shutil, sys
from pathlib import Path
from PySide6.QtCore import QProcess, QTimer
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QComboBox,QPlainTextEdit,QMessageBox,QFileDialog,QGroupBox,QListWidget,QListWidgetItem,QFrame,QSizeGrip)
from appearance import STYLE, Titlebar
from PySide6.QtCore import Qt
from core import create_project, TEMPLATES
class Hub(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle('Laccaz · Dev Hub');self.resize(1180,820);self.setMinimumSize(920,680);self.setWindowFlags(Qt.Window|Qt.FramelessWindowHint)
  self.current=Path.home();self.proc=None
  w=QWidget();self.setCentralWidget(w);outer=QVBoxLayout(w);outer.setContentsMargins(16,12,16,10);outer.addWidget(Titlebar(self,'Dev Hub'))
  split=QHBoxLayout();outer.addLayout(split)
  side=QWidget();side.setObjectName('sidebar');side.setFixedWidth(220);nav=QVBoxLayout(side);nav.setContentsMargins(18,24,18,20);split.addWidget(side)
  logo=QLabel('Dev Hub');logo.setObjectName('brand');nav.addWidget(logo);sub=QLabel('Laccaz workspace');sub.setObjectName('muted');nav.addWidget(sub);nav.addSpacing(24)
  for label,fn in [('+ Новый проект',lambda:self.name.setFocus()),('Открыть папку…',self.choose),('Редактор кода',lambda:self.launch('kate',str(self.current))),('Терминал',lambda:self.launch('konsole','--workdir',str(self.current)))]:
   bt=QPushButton(label);bt.clicked.connect(fn);nav.addWidget(bt)
  nav.addSpacing(20);nav.addWidget(QLabel('ВАШИ ПРОЕКТЫ'));self.recent=QListWidget();self.recent.itemClicked.connect(self.select_recent);nav.addWidget(self.recent);self.refresh_projects()
  main=QWidget();v=QVBoxLayout(main);v.setContentsMargins(26,12,10,0);v.setSpacing(15);split.addWidget(main,1)
  title=QLabel('Создавай. Запускай. Развивай.');title.setObjectName('hero');title.setWordWrap(True);v.addWidget(title)
  self.location=QLabel();self.location.setObjectName('muted');self.location.setWordWrap(True);v.addWidget(self.location)
  box=QGroupBox('Новый проект');r=QHBoxLayout(box);self.name=QLineEdit();self.name.setPlaceholderText('Название проекта');r.addWidget(self.name,1);self.lang=QComboBox();self.lang.addItems(TEMPLATES);r.addWidget(self.lang);bt=QPushButton('Создать');bt.setObjectName('primary');bt.clicked.connect(self.create);r.addWidget(bt);v.addWidget(box)
  row=QHBoxLayout();v.addLayout(row)
  for label,cmd in [('Python venv',['python3','-m','venv','.venv']),('Git init',['git','init']),('Git status',['git','status','--short','--branch']),('Docker',['docker','ps'])]:
   bt=QPushButton(label);bt.clicked.connect(lambda checked=False,c=cmd:self.run(c));row.addWidget(bt)
  label=QLabel('КОНСОЛЬ ПРОЕКТА');label.setObjectName('muted');v.addWidget(label)
  self.output=QPlainTextEdit();self.output.setReadOnly(True);self.output.setMaximumBlockCount(5000);self.output.setPlaceholderText('Результат запуска появится здесь.');v.addWidget(self.output,1)
  row=QHBoxLayout();self.command=QLineEdit();self.command.setPlaceholderText('Команда: python3 main.py');self.command.returnPressed.connect(self.custom);row.addWidget(self.command,1)
  bt=QPushButton('Запустить');bt.setObjectName('primary');bt.clicked.connect(self.custom);row.addWidget(bt);bt=QPushButton('Стоп');bt.clicked.connect(self.stop);row.addWidget(bt);v.addLayout(row)
  row=QHBoxLayout();v.addLayout(row)
  for label,fn in [('Файлы проекта',lambda:self.launch('dolphin',str(self.current))),('Проверить инструменты',lambda:self.run(['laccaz-doctor']))]:
   bt=QPushButton(label);bt.clicked.connect(fn);row.addWidget(bt)
  bottom=QHBoxLayout();bottom.addStretch();bottom.addWidget(QSizeGrip(self));outer.addLayout(bottom);self.update_path()
 def refresh_projects(self):
  self.recent.clear();root=Path.home()/'Projects'
  if root.exists():
   for p in sorted(root.iterdir()):
    if p.is_dir():item=QListWidgetItem(p.name);item.setData(Qt.UserRole,str(p));self.recent.addItem(item)
 def select_recent(self,item):self.current=Path(item.data(Qt.UserRole));self.update_path()
 def update_path(self): self.location.setText('ПРОЕКТ  /  '+str(self.current))
 def choose(self):
  d=QFileDialog.getExistingDirectory(self,'Открыть проект',str(Path.home()/'Projects'))
  if d:self.current=Path(d);self.update_path()
 def create(self):
  try:
   self.current=create_project(Path.home()/'Projects',self.name.text().strip(),self.lang.currentText());self.update_path();self.refresh_projects();self.output.appendPlainText('Создан: '+str(self.current))
  except Exception as e: QMessageBox.warning(self,'Проект',str(e))
 def launch(self,program,*args):
  result=QProcess.startDetached(program,list(args))
  if not (result[0] if isinstance(result,tuple) else result): QMessageBox.warning(self,'Запуск','Не удалось открыть '+program)
 def custom(self):
  try:cmd=shlex.split(self.command.text())
  except ValueError as e:QMessageBox.warning(self,'Команда',str(e));return
  if cmd:self.run(cmd)
 def run(self,cmd):
  if self.proc is not None: QMessageBox.information(self,'Процесс','Сначала дождись завершения или нажми Остановить.');return
  self.output.appendPlainText('\n$ '+shlex.join(cmd));p=QProcess(self);self.proc=p;p.setWorkingDirectory(str(self.current));p.setProcessChannelMode(QProcess.MergedChannels)
  p.readyReadStandardOutput.connect(lambda:self.output.appendPlainText(bytes(p.readAllStandardOutput()).decode(errors='replace').rstrip()))
  p.finished.connect(lambda code,status:self.done(p,code));p.errorOccurred.connect(lambda error:self.failed(p,error));p.start(cmd[0],cmd[1:])
 def failed(self,p,error):
  self.output.appendPlainText(p.errorString())
  if error==QProcess.FailedToStart:self.proc=None;p.deleteLater()
 def done(self,p,code):
  self.output.appendPlainText('Код завершения: '+str(code));self.proc=None;p.deleteLater()
 def stop(self):
  if self.proc:
   p=self.proc;p.terminate();QTimer.singleShot(2000,lambda:p.kill() if self.proc is p else None)
 def closeEvent(self,event):
  if self.proc:
   QMessageBox.information(self,'Процесс','Останови команду перед закрытием.');event.ignore()
  else:event.accept()
if __name__=='__main__':
 app=QApplication(sys.argv);app.setStyle('Fusion');app.setStyleSheet(STYLE)
 h=Hub();h.show();sys.exit(app.exec())
