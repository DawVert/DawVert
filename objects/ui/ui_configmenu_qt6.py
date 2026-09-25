from PyQt6 import QtWidgets, uic, QtCore, QtGui

from PyQt6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
	QMetaObject, QObject, QPoint, QRect,
	QSize, QTime, QUrl, Qt)
from PyQt6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
	QFont, QFontDatabase, QGradient, QIcon,
	QImage, QKeySequence, QLinearGradient, QPainter,
	QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
	QGridLayout, QGroupBox, QHBoxLayout, QLabel,
	QLayout, QLineEdit, QMainWindow, QSizePolicy,
	QSpinBox, QVBoxLayout, QWidget, QFormLayout)

import functools

class ConfigWindow(QWidget):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setObjectName("Form")
		self.resize(32, 32)
		self.layout_group = QHBoxLayout()
		self.layout_group.setObjectName("layout_group")
		self.setLayout(self.layout_group)
		#sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
		#sizePolicy1.setHorizontalStretch(0)
		#sizePolicy1.setVerticalStretch(0)
		#sizePolicy1.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
		#self.layout_group.setSizePolicy(sizePolicy1)
		#self.centrallayout = QHBoxLayout(self.layout_group)
		#self.centrallayout.setObjectName(u"centrallayout")
		#self.centrallayout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)

		self.all_groupbox = []
		self.all_gridLayout = []
		self.dict = {}

		self.callb_name = None
		self.callb_func = None

	def add_group(self, name, label):
		self.groupBox = QGroupBox()

		self.groupBox.setObjectName(u"groupBox_"+name)
		self.groupBox.setTitle(label)
		self.groupBox.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
		self.groupBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
		sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
		sizePolicy2.setHorizontalStretch(0)
		sizePolicy2.setVerticalStretch(0)
		sizePolicy2.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
		self.groupBox.setSizePolicy(sizePolicy2)
		self.layout_group.addWidget(self.groupBox)
		self.current_groupbox = self.groupBox

		self.layout_grid = QGridLayout()
		self.layout_grid.setObjectName(u"gridLayout_"+name)
		self.layout_grid.setSpacing(6)
		self.layout_grid.setObjectName("gridLayout")
		self.groupBox.setLayout(self.layout_grid)
		self.current_gridlayout = self.layout_grid

		self.all_groupbox.append(self.groupBox)
		self.all_gridLayout.append(self.layout_grid)

		self.current_count = 0

		self.controls = []

	def load_dict(self, indata):
		self.dict = indata if indata is not None else {}

	def premake_hl(self, name, data):
		self.temp_layout = QHBoxLayout()
		self.temp_layout.setObjectName(u"layout_"+name)
		self.temp_layout.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
		self.temp_label = QLabel(self.current_groupbox)
		self.temp_label.setObjectName(u"label_"+name)
		self.temp_label.setText(data.name if data.name else name)

		self.temp_layout.addWidget(self.temp_label)

		self.current_gridlayout.addLayout(self.temp_layout, self.current_count, 0, 1, 1)
		self.current_count += 1
		return self.temp_layout

	def gen_sizePolicy(self):
		sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Maximum)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		return sizePolicy

	def add_control_text(self, name, data):
		sizePolicy = self.gen_sizePolicy()

		self.control = QLineEdit(self.current_groupbox)
		self.control.setObjectName(u"editor_"+name)
		sizePolicy.setHeightForWidth(self.control.sizePolicy().hasHeightForWidth())
		self.control.setSizePolicy(sizePolicy)
		self.temp_layout = self.premake_hl(name, data)
		self.temp_layout.addWidget(self.control)
		self.control.textChanged.connect(functools.partial(self.set_value, name))
		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval: self.control.setText(inval)
		self.controls.append(self.control)

	def add_control_int(self, name, data):
		sizePolicy = self.gen_sizePolicy()

		val_lower = data.value_min if data.value_min is not None else -10000
		val_upper = data.value_max if data.value_max is not None else 10000

		self.control = QSpinBox(self.groupBox)
		self.control.setObjectName(u"editor_"+name)
		self.control.setRange(val_lower, val_upper)
		sizePolicy.setHeightForWidth(self.control.sizePolicy().hasHeightForWidth())
		self.control.setSizePolicy(sizePolicy)
		self.temp_layout = self.premake_hl(name, data)
		self.temp_layout.addWidget(self.control)
		self.control.valueChanged.connect(functools.partial(self.set_value, name))
		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval: self.control.setValue(int(inval))
		self.controls.append(self.control)

	def add_control_float(self, name, data):
		sizePolicy = self.gen_sizePolicy()

		val_lower = data.value_min if data.value_min is not None else -10000
		val_upper = data.value_max if data.value_max is not None else 10000
		val_step = data.value_step if data.value_step is not None else 0.05

		self.control = QDoubleSpinBox(self.groupBox)
		self.control.setObjectName(u"editor_"+name)
		self.control.setRange(val_lower, val_upper)
		self.control.setSingleStep(val_step)
		sizePolicy.setHeightForWidth(self.control.sizePolicy().hasHeightForWidth())
		self.control.setSizePolicy(sizePolicy)
		self.temp_layout = self.premake_hl(name, data)
		self.temp_layout.addWidget(self.control)
		self.control.valueChanged.connect(functools.partial(self.set_value, name))
		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval: self.control.setValue(float(inval))
		self.controls.append(self.control)

	def add_control_bool(self, name, data):
		sizePolicy = self.gen_sizePolicy()

		self.control = QCheckBox(self.groupBox)
		self.control.setObjectName(u"editor_"+name)
		self.control.setText(data.name if data.name else name)

		self.layout_grid.addWidget(self.control, self.current_count, 0, 1, 1)
		self.control.stateChanged.connect(functools.partial(self.set_value_check, name))

		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval: self.control.setChecked(bool(inval))
		self.controls.append(self.control)

		self.current_count += 1

	def add_control_enum(self, name, data):
		sizePolicy = self.gen_sizePolicy()

		self.control = QComboBox(self.groupBox)
		self.control.setObjectName(u"editor_"+name)
		sizePolicy.setHeightForWidth(self.control.sizePolicy().hasHeightForWidth())
		self.control.setSizePolicy(sizePolicy)
		self.temp_layout = self.premake_hl(name, data)
		self.temp_layout.addWidget(self.control)
		for choice_obj in data.choices: self.control.addItem(choice_obj.name)
		inval = None

		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		valnames = dict([[x.id, n] for n, x in enumerate(data.choices)])
		if inval in valnames: self.control.setCurrentIndex(valnames[inval])

		self.control.currentIndexChanged.connect(functools.partial(self.set_value_combo, name, data))

		self.controls.append(self.control)

	def showui(self):
		self.show()

	def set_value(self, key, value):
		self.dict[key] = value
		if self.callb_func: self.callb_func(self.callb_name, key, value)

	def set_value_combo(self, key, data, value):
		self.dict[key] = data.choices[value].id
		if self.callb_func: self.callb_func(self.callb_name, key, data.choices[value].id)

	def set_value_check(self, key, value):
		self.dict[key] = bool(value)
		if self.callb_func: self.callb_func(self.callb_name, key, bool(value))

def show_gui(miniconfmenu_store_obj, dictval, windowtitle, callb_name, callb_func):
	if miniconfmenu_store_obj.parts:
		sepparts = {}
		for k, v in miniconfmenu_store_obj.parts.items():
			groupname = v.group
			if groupname not in sepparts: sepparts[groupname] = {}
			sepparts[groupname][k] = v

		window = ConfigWindow()
		window.load_dict(dictval)
		window.setWindowTitle(windowtitle)
		window.callb_name = callb_name
		window.callb_func = callb_func

		groupnames = miniconfmenu_store_obj.groupnames

		for k, v in sepparts.items():
			window.add_group(k, groupnames[k] if k in groupnames else k)
			for vk, vv in v.items():
				proptype = vv.type
				if proptype=='text': window.add_control_text(vk, vv)
				if proptype=='int': window.add_control_int(vk, vv)
				if proptype=='float': window.add_control_float(vk, vv)
				if proptype=='bool': window.add_control_bool(vk, vv)
				if proptype=='enum': window.add_control_enum(vk, vv)

		window.show()

		return window.dict
	else:
		return dictval