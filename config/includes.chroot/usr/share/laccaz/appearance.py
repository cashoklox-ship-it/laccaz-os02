from PySide6.QtCore import Qt
from PySide6.QtGui import QColor,QPainter,QPen,QPixmap,QIcon,QLinearGradient
from PySide6.QtWidgets import QWidget,QHBoxLayout,QPushButton,QLabel
STYLE="""
QWidget{background:#f3f5f9;color:#202738;font-family:DejaVu Sans;font-size:13px}
QLabel{background:transparent} QLabel#brand{font-size:24px;font-weight:700;color:#29364e}
QLabel#hero{font-size:34px;font-weight:700} QLabel#muted{color:#758095}
QWidget#sidebar{background:#e5eaf3;border-radius:18px} QWidget#card{background:white;border:1px solid #e2e7f0;border-radius:18px}
QPushButton{background:#fff;border:1px solid #dfe4ed;border-radius:11px;padding:11px 15px;text-align:left}
QPushButton:hover{background:#e7edff;border-color:#b6c9fa} QPushButton:pressed{background:#d5e1ff}
QPushButton#primary{background:#3578ef;color:white;border:0;font-weight:600} QPushButton#primary:hover{background:#2569db}
QLineEdit,QComboBox{background:white;border:1px solid #dde3ec;border-radius:11px;padding:12px;selection-background-color:#b8d4ff}
QPlainTextEdit{background:#172032;color:#d6e3f7;border:0;border-radius:14px;padding:14px;font-family:monospace}
QListWidget{background:#fff;border:1px solid #e4e8f0;border-radius:15px;padding:9px}
QListWidget::item{padding:15px;border-bottom:1px solid #edf0f5}
QListWidget::item:selected{background:#e3edff;color:#2456a5;border-radius:8px}
QGroupBox{background:white;border:1px solid #e2e7f0;border-radius:16px;margin-top:16px;padding:20px}
QGroupBox::title{subcontrol-origin:margin;left:20px;padding:0 6px}
QCheckBox{padding:9px} QScrollBar:vertical{width:9px;background:transparent} QScrollBar::handle:vertical{background:#bac4d4;border-radius:4px;min-height:25px}
"""
class Titlebar(QWidget):
 def __init__(self,window,title):
  super().__init__();self.window=window;row=QHBoxLayout(self);row.setContentsMargins(8,6,8,6)
  for color,fn in [('#ff6059',window.close),('#ffbd2e',window.showMinimized),('#28c840',self.zoom)]:
   button=QPushButton();button.setFixedSize(14,14);button.setToolTip({'#ff6059':'Закрыть','#ffbd2e':'Свернуть','#28c840':'Развернуть'}[color]);button.setStyleSheet('QPushButton{background:'+color+';border:1px solid rgba(0,0,0,25);border-radius:7px;padding:0}');button.clicked.connect(fn);row.addWidget(button)
  row.addSpacing(15);row.addWidget(QLabel(title));row.addStretch()
 def zoom(self):self.window.showNormal() if self.window.isMaximized() else self.window.showMaximized()
 def mousePressEvent(self,event):
  if event.button()==Qt.LeftButton and self.window.windowHandle():self.window.windowHandle().startSystemMove()
 def mouseDoubleClickEvent(self,event):self.zoom()

def dock_icon(kind,index):
 pix=QPixmap(48,48);pix.fill(Qt.transparent);p=QPainter(pix);p.setRenderHint(QPainter.Antialiasing)
 colors=['#586bef','#8763dc','#4099e0','#34435c','#39aaa3','#ef9760'];g=QLinearGradient(0,0,48,48);g.setColorAt(0,QColor(colors[index]));g.setColorAt(1,QColor(colors[index]).darker(125));p.setPen(Qt.NoPen);p.setBrush(g);p.drawRoundedRect(0,0,48,48,12,12);p.setPen(QPen(QColor('white'),2.3));p.setBrush(Qt.NoBrush)
 if index==0:
  for x in (13,24,35):
   for y in (13,24,35):p.drawEllipse(x-2,y-2,4,4)
 elif index==1:
  p.drawLine(18,14,10,24);p.drawLine(10,24,18,34);p.drawLine(30,14,38,24);p.drawLine(38,24,30,34);p.drawLine(27,11,21,37)
 elif index==2:
  p.drawRoundedRect(9,16,31,23,3,3);p.drawLine(10,16,10,11);p.drawLine(10,11,23,11);p.drawLine(23,11,28,16)
 elif index==3:
  p.drawLine(12,15,21,23);p.drawLine(21,23,12,31);p.drawLine(25,33,36,33)
 elif index==4:
  p.drawRoundedRect(12,11,25,29,3,3);p.drawRoundedRect(19,8,11,7,2,2);p.drawLine(18,24,31,24);p.drawLine(18,31,31,31)
 else:
  p.drawRoundedRect(8,10,25,22,3,3);p.drawRoundedRect(16,20,25,20,3,3)
 p.end();return QIcon(pix)
