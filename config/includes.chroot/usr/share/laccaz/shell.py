#!/usr/bin/python3
import configparser, os, shutil, sys
from pathlib import Path
from PySide6.QtCore import Qt,QTimer,QProcess,QDateTime,QUrl,QSize
from PySide6.QtGui import QPainter,QColor,QPen,QFont,QDesktopServices,QLinearGradient,QPainterPath
from PySide6.QtWidgets import QApplication,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QListWidget,QListWidgetItem,QStackedWidget,QMessageBox,QCheckBox,QFrame,QSizePolicy
from appearance import STYLE, Titlebar, dock_icon

def start(program,args=[]):
 ok=QProcess.startDetached(program,args)
 return ok[0] if isinstance(ok,tuple) else ok

def applications():
 found={}
 roots=[Path.home()/'.local/share/applications',Path('/usr/local/share/applications'),Path('/usr/share/applications')]
 seen=set()
 for root in roots:
  for p in sorted(root.glob('**/*.desktop')):
   desktop_id=str(p.relative_to(root)).replace('/','-')
   if desktop_id in seen:continue
   seen.add(desktop_id)
   try:
    c=configparser.ConfigParser(interpolation=None,strict=False);c.read(p);e=c['Desktop Entry']
    if e.get('Type')!='Application' or e.get('NoDisplay','false')=='true' or e.get('Hidden','false')=='true':continue
    if 'OnlyShowIn' in e and not any(x in ('Laccaz','KDE') for x in e['OnlyShowIn'].split(';')):continue
    if 'Laccaz' in e.get('NotShowIn','').split(';'):continue
    if e.get('TryExec') and not shutil.which(e['TryExec']):continue
    name=e.get('Name[ru]',e.get('Name',p.stem));found[desktop_id]=(name,str(p))
   except Exception:continue
 return sorted(found.values(),key=lambda x:x[0].casefold())
class Dock(QWidget):
 def paintEvent(self,event):
  p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);p.setPen(QPen(QColor(255,255,255,210),1));p.setBrush(QColor(243,246,255,210));p.drawRoundedRect(self.rect().adjusted(1,1,-1,-1),23,23);p.end()
class Backdrop(QWidget):
 def paintEvent(self,event):
  p=QPainter(self);p.setRenderHint(QPainter.Antialiasing);w,h=self.width(),self.height()
  g=QLinearGradient(0,0,w,h);g.setColorAt(0,QColor('#86b7e4'));g.setColorAt(.45,QColor('#c2d3ef'));g.setColorAt(1,QColor('#f5c9be'));p.fillRect(self.rect(),g)
  for i,color in enumerate(['#668bce','#8ba9e1','#b1c0e8','#d8ceec']):
   path=QPainterPath();path.moveTo(-100,h*(.55+i*.12));path.cubicTo(w*.22,h*(-.25+i*.12),w*.62,h*(1.2+i*.08),w+100,h*(.18+i*.2));path.lineTo(w+100,h+100);path.lineTo(-100,h+100);path.closeSubpath();p.fillPath(path,QColor(color))
  p.end()
class Shell:
 def __init__(self,preview=False):
  self.preview=preview;self.folder=Path.home();self.history=[];self.apps=applications();self.root=Backdrop();self.root.setWindowTitle('Laccaz Surface');self.root.setWindowFlags(Qt.FramelessWindowHint)
  geo=QApplication.primaryScreen().geometry();self.root.setGeometry(geo)
  self.panel=Dock();self.panel.setObjectName('dock');self.panel.setStyleSheet('QWidget#dock{background:rgba(242,246,255,225);border:1px solid rgba(255,255,255,200);border-radius:23px}');self.panel.setWindowTitle('Laccaz Dock');self.panel.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.panel.setAttribute(Qt.WA_TranslucentBackground)
  rail=QHBoxLayout(self.panel);rail.setContentsMargins(13,10,13,10);rail.setSpacing(8)
  for index,(name,fn) in enumerate([('▦',lambda:self.show('apps')),('⌘',lambda:start('laccaz-devhub')),('▱',lambda:self.show('files')),('>_',lambda:start('konsole')),('▤',lambda:self.show('clips')),('◫',lambda:self.show('windows'))]):
   bt=QPushButton();bt.setIcon(dock_icon(name,index));bt.setIconSize(QSize(48,48));bt.setFixedSize(60,58);bt.setStyleSheet('QPushButton{font-size:25px;text-align:center;border-radius:15px;background:#ffffff;border:1px solid #d5deed} QPushButton:hover{background:#dbe9ff}');bt.setToolTip({'▦':'Приложения','⌘':'Dev Hub','▱':'Файлы','>_':'Терминал','▤':'Буфер обмена','◫':'Окна'}[name]);bt.clicked.connect(fn);rail.addWidget(bt)
  self.panel.adjustSize();self.panel.move(geo.x()+(geo.width()-self.panel.width())//2,geo.y()+geo.height()-self.panel.height()-14)
  self.bar=QWidget();self.bar.setWindowTitle('Laccaz Menu');self.bar.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.bar.setGeometry(geo.x(),geo.y(),geo.width(),38);self.bar.setStyleSheet('QWidget{background:#e7edf9;color:#29374c} QPushButton{border:0;background:transparent;padding:5px 12px;border-radius:7px}')
  menu=QHBoxLayout(self.bar);menu.setContentsMargins(18,0,18,0)
  for name,fn in [('Laccaz',self.home),('Проекты',lambda:self.show('projects')),('Приложения',lambda:self.show('apps')),('Окна',lambda:self.show('windows'))]:
   bt=QPushButton(name);bt.clicked.connect(fn);menu.addWidget(bt)
  menu.addStretch();self.clock=QLabel();menu.addWidget(self.clock);bt=QPushButton('Выход');bt.clicked.connect(self.logout);menu.addWidget(bt)
  self.drawer=QWidget();self.drawer.setWindowTitle('Laccaz Search');self.drawer.setWindowFlags(Qt.Tool|Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint);self.drawer.resize(min(710,geo.width()-40),min(660,geo.height()-150));self.drawer.move(geo.x()+(geo.width()-self.drawer.width())//2,geo.y()+65)
  d=QVBoxLayout(self.drawer);d.setContentsMargins(24,18,24,24);d.setSpacing(14);d.addWidget(Titlebar(self.drawer,'Laccaz'));self.title=QLabel();self.title.setObjectName('brand');d.addWidget(self.title)
  self.search=QLineEdit();self.search.setPlaceholderText('Поиск…');self.search.textChanged.connect(self.populate);d.addWidget(self.search)
  self.list=QListWidget();self.list.itemActivated.connect(self.activate);self.list.itemClicked.connect(self.activate);d.addWidget(self.list)
  self.pause=QCheckBox('Пауза записи буфера');d.addWidget(self.pause)
  self.clearbutton=QPushButton('Очистить историю и системный буфер');self.clearbutton.clicked.connect(self.clear);d.addWidget(self.clearbutton)
  self.note=QLabel();self.note.setWordWrap(True);self.note.setObjectName('muted');d.addWidget(self.note)
  QApplication.clipboard().dataChanged.connect(self.clip_changed)
  self.timer=QTimer();self.timer.timeout.connect(self.tick);self.timer.start(1000);self.tick();self.root.show();self.panel.show();self.bar.show()
  if not preview:QTimer.singleShot(100,self.properties)
 def properties(self):
  if not os.environ.get('DISPLAY'):return
  def prop(widget,key,kind,value):start('xprop',['-id',str(int(widget.winId())),'-f',key,kind,'-set',key,value])
  prop(self.root,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DESKTOP');prop(self.panel,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DOCK')
  prop(self.bar,'_NET_WM_WINDOW_TYPE','32a','_NET_WM_WINDOW_TYPE_DOCK')
  prop(self.panel,'_NET_WM_STRUT_PARTIAL','32c',f'0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, {self.root.width()-1}')
  prop(self.bar,'_NET_WM_STRUT_PARTIAL','32c',f'0, 0, 38, 0, 0, 0, 0, 0, 0, {self.root.width()-1}, 0, 0');self.root.lower()
 def tick(self):self.clock.setText(QDateTime.currentDateTime().toString('hh:mm   /   dd.MM.yyyy'))
 def home(self):self.drawer.hide();self.root.raise_();QTimer.singleShot(10,self.root.lower)
 def show(self,mode):
  self.mode=mode;self.search.clear();self.title.setText({'apps':'Приложения','clips':'Буфер обмена','projects':'Проекты','windows':'Окна','files':'Файлы'}[mode]);self.pause.setVisible(mode=='clips');self.clearbutton.setVisible(mode=='clips');self.populate();self.drawer.show();self.drawer.raise_();self.drawer.activateWindow();self.search.setFocus()
 def populate(self):
  if not hasattr(self,'mode'):return
  self.list.clear();q=self.search.text().casefold();rows=[]
  if self.mode=='apps':rows=[(n,p) for n,p in self.apps];self.note.setText('Поиск установленных приложений. Запуск по нажатию.')
  elif self.mode=='clips':rows=[(s,s) for s in self.history];self.note.setText('Только текст • до 40 записей в памяти • на диск не сохраняется. Выбери фрагмент, затем вставь Ctrl+V. Для паролей включай паузу.')
  elif self.mode=='files':
   self.note.setText(str(self.folder)+' • выбери папку или файл')
   try:rows=[('↑ На уровень выше',str(self.folder.parent))]+[(('▸ ' if p.is_dir() else '')+p.name,str(p)) for p in sorted(self.folder.iterdir(),key=lambda p:(not p.is_dir(),p.name.casefold())) if not p.name.startswith('.')]
   except OSError as e:self.note.setText(str(e));rows=[]
  elif self.mode=='projects':
   root=Path.home()/'Projects';root.mkdir(exist_ok=True);rows=[(p.name,str(p)) for p in sorted(root.iterdir()) if p.is_dir()];rows.insert(0,('+ Создать проект в Dev Hub','NEW'));self.note.setText('Проекты из ~/Projects. Выбор открывает папку.')
  else:
   self.note.setText('Выбери окно для переключения. Alt+Tab также работает.');self.windows();return
  for label,value in rows:
   if q in label.casefold():item=QListWidgetItem(label[:180]);item.setData(Qt.UserRole,value);self.list.addItem(item)
 def windows(self):
  p=QProcess(self.drawer);p.finished.connect(lambda code,status:self.window_result(p));p.start('wmctrl',['-l'])
 def window_result(self,p):
  if self.mode=='windows':
   for line in bytes(p.readAllStandardOutput()).decode(errors='replace').splitlines():
    parts=line.split(None,3)
    if len(parts)==4 and not parts[3].startswith('Laccaz ') and self.search.text().casefold() in parts[3].casefold():
     it=QListWidgetItem(parts[3]);it.setData(Qt.UserRole,parts[0]);self.list.addItem(it)
  p.deleteLater()
 def activate(self,item):
  value=item.data(Qt.UserRole)
  if self.mode=='apps':
   if not start('gio',['launch',value]):QMessageBox.warning(self.drawer,'Запуск','Не удалось запустить приложение.');return
  elif self.mode=='clips':QApplication.clipboard().setText(value)
  elif self.mode=='files':
   p=Path(value)
   if p.is_dir():self.folder=p;self.search.clear();self.populate();return
   QDesktopServices.openUrl(QUrl.fromLocalFile(value))
  elif self.mode=='projects':
   if value=='NEW':start('laccaz-devhub')
   else:QDesktopServices.openUrl(QUrl.fromLocalFile(value))
  else:start('wmctrl',['-ia',value])
  self.drawer.hide()
 def clip_changed(self):
  if self.pause.isChecked():return
  mime=QApplication.clipboard().mimeData()
  if not mime or mime.hasFormat('x-kde-passwordManagerHint') or not mime.hasText():return
  s=mime.text()
  if not s.strip() or len(s)>20000:return
  if s in self.history:self.history.remove(s)
  self.history.insert(0,s);del self.history[40:]
  if self.drawer.isVisible() and getattr(self,'mode','')=='clips':self.populate()
 def clear(self):self.history.clear();QApplication.clipboard().clear();self.populate()
 def logout(self):
  if QMessageBox.question(self.panel,'Завершить сеанс','Закрыть оболочку и выйти из сеанса?')==QMessageBox.Yes:QApplication.quit()
if __name__=='__main__':
 app=QApplication(sys.argv);app.setQuitOnLastWindowClosed(False);app.setStyle('Fusion');app.setStyleSheet(STYLE);shell=Shell('--preview' in sys.argv);sys.exit(app.exec())
