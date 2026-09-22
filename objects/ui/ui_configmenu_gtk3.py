import gi
import functools

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class ConfigWindow(Gtk.Window):
	def __init__(self, windowtitle):
		super().__init__(title=windowtitle)
		self.set_border_width(3)

		self.notebook = Gtk.Notebook()
		self.add(self.notebook)
		self.dict = {}
		self.count = 0

	def add_group(self, name, labeltxt):
		notepage = Gtk.Box()
		notepage.set_border_width(10)
		self.notebook.append_page(notepage, Gtk.Label(label=labeltxt))
		self.current_page = notepage

		self.grid = Gtk.Grid()
		self.grid.set_column_spacing(4)
		self.grid.set_row_spacing(4)
		notepage.add(self.grid)

		self.count = 0
		return notepage

	def load_dict(self, indata):
		self.dict = indata if indata is not None else {}

	def add_control_text(self, name, data):
		labelname = data.name if data.name else name
		label = Gtk.Label(label=labelname)
		control = Gtk.Entry()

		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval is not None: control.set_text(inval)

		control.connect("changed", functools.partial(self.set_value_entry, name))

		self.grid.attach(label, 0, self.count, 1, 1)
		self.grid.attach(control, 1, self.count, 2, 1)
		self.count += 1

	def add_control_int(self, name, data):
		labelname = data.name if data.name else name
		label = Gtk.Label(label=labelname)
		control = Gtk.SpinButton()

		val_lower = data.value_min if data.value_min is not None else -10000
		val_upper = data.value_max if data.value_max is not None else 10000
		adjustment = Gtk.Adjustment(lower=val_lower, upper=val_upper, step_increment=1, page_increment=10)
		control.set_adjustment(adjustment)

		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval is not None: control.set_value(inval)

		control.connect("changed", functools.partial(self.set_value_int, name))

		self.grid.attach(label, 0, self.count, 1, 1)
		self.grid.attach(control, 1, self.count, 2, 1)
		self.count += 1

	def add_control_float(self, name, data):
		labelname = data.name if data.name else name
		label = Gtk.Label(label=labelname)
		control = Gtk.SpinButton()

		val_lower = data.value_min if data.value_min is not None else -10000
		val_upper = data.value_max if data.value_max is not None else 10000
		adjustment = Gtk.Adjustment(lower=val_lower, upper=val_upper, step_increment=1, page_increment=10)
		control.set_adjustment(adjustment)

		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval is not None: control.set_value(inval)

		control.connect("changed", functools.partial(self.set_value_float, name))

		self.grid.attach(label, 0, self.count, 1, 1)
		self.grid.attach(control, 1, self.count, 2, 1)
		self.count += 1

	def add_control_bool(self, name, data):
		labelname = data.name if data.name else name
		label = Gtk.Label(label=labelname)
		control = Gtk.CheckButton()

		inval = None
		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		if inval is not None: control.set_active(inval)

		control.connect("toggled", functools.partial(self.set_value_check, name))

		self.grid.attach(label, 0, self.count, 1, 1)
		self.grid.attach(control, 1, self.count, 2, 1)
		self.count += 1

	def add_control_enum(self, name, data):
		labelname = data.name if data.name else name
		label = Gtk.Label(label=labelname)

		controlstorage = Gtk.ListStore(int, str)
		for n, choice_obj in enumerate(data.choices): 
			controlstorage.append([n, choice_obj.name])

		control = Gtk.ComboBox.new_with_model_and_entry(controlstorage)
		renderer_text = Gtk.CellRendererText()
		control.pack_start(renderer_text, True)
		control.add_attribute(renderer_text, "text", 0)
		control.set_entry_text_column(1)

		if name in self.dict: inval = self.dict[name]
		elif data.value_def: inval = data.value_def
		valnames = dict([[x.id, n] for n, x in enumerate(data.choices)])
		if inval in valnames: control.set_active(valnames[inval])

		control.connect("changed", functools.partial(self.set_value_combo, name, data))

		self.grid.attach(label, 0, self.count, 1, 1)
		self.grid.attach(control, 1, self.count, 2, 1)
		self.count += 1

	def set_value_entry(self, key, control):
		self.dict[key] = control.get_text()

	def set_value_int(self, key, control):
		self.dict[key] = control.get_value_as_int()

	def set_value_float(self, key, control):
		self.dict[key] = control.get_value()

	def set_value_combo(self, key, data, control):
		tree_iter = control.get_active_iter()
		if tree_iter is not None:
			model = control.get_model()
			row_id, name = model[tree_iter][:2]
			self.dict[key] = data.choices[row_id].id

	def set_value_check(self, key, control):
		self.dict[key] = control.get_active()

def show_gui(miniconfmenu_store_obj, dictval, windowtitle):
	if miniconfmenu_store_obj.parts:
		sepparts = {}
		for k, v in miniconfmenu_store_obj.parts.items():
			groupname = v.group
			if groupname not in sepparts: sepparts[groupname] = {}
			sepparts[groupname][k] = v

		groupnames = miniconfmenu_store_obj.groupnames

		window = ConfigWindow(windowtitle)
		window.load_dict(dictval)
		window.connect("destroy", Gtk.main_quit)

		for k, v in sepparts.items():
			window.add_group(k, groupnames[k] if k in groupnames else k)
			for vk, vv in v.items():
				proptype = vv.type
				if proptype=='text': window.add_control_text(vk, vv)
				if proptype=='int': window.add_control_int(vk, vv)
				if proptype=='float': window.add_control_float(vk, vv)
				if proptype=='bool': window.add_control_bool(vk, vv)
				if proptype=='enum': window.add_control_enum(vk, vv)

		window.show_all()
		Gtk.main()