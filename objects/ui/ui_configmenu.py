
import json

class miniconfmenu_storepart_choice():
	def __init__(self):
		self.name = None
		self.id = None

	def read_dict(self, d):
		self.id = d['id']
		self.name = d['name'] if 'name' in d else self.id

class miniconfmenu_storepart():
	def __init__(self):
		self.type = None
		self.name = ''
		self.value_def = None
		self.value_min = None
		self.value_max = None
		self.group = 'main'
		self.choices = None

	def read_dict(self, d):
		if 'type' in d: self.type = d['type']
		if 'name' in d: self.name = d['name']
		if 'def' in d: self.value_def = d['def']
		if 'min' in d: self.value_min = d['min']
		if 'max' in d: self.value_max = d['max']
		if 'group' in d: self.group = d['group']
		if 'choices' in d: 
			self.choices = []
			for x in d['choices']:
				choice_obj = miniconfmenu_storepart_choice()
				choice_obj.read_dict(x)
				self.choices.append(choice_obj)

class miniconfmenu_store():
	def __init__(self):
		self.parts = {}

	def json_load(self, filename):
		f = open(filename)

	def dict_load(self, d):
		if d is not None:
			for k, v in d.items():
				storepart = miniconfmenu_storepart()
				storepart.read_dict(v)
				self.parts[k] = storepart
