# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import dataclasses
from dataclasses import dataclass
from dataclasses import dataclass, field

class globalstate:
	debug_alld = {}
	debug_allp = {}
	globalids = {}
	classes = {}

	def reset():
		debug_alld = {}
		debug_allp = {}
		globalids = {}

# ================================================ CREATE ================================================

def to_wide_string(textd):
	o = cubasexml_string(None)
	o.text = textd
	o.wide = True
	return o

def to_norm_string(textd):
	o = cubasexml_string(None)
	o.text = textd
	return o

def add_list(list, classname):
	o = globalstate.classes[classname]()
	list.append(o)
	return o

def add_list_genid(list, classname, counter_obj):
	o = globalstate.classes[classname]()
	o.idnum = counter_obj.get()
	list.append(o)
	return o

# ================================================ OBJECTS ================================================

class cubasexml_string:
	def __init__(self, indata):
		self.text = None
		self.wide = False
		if indata is not None: self.read(indata)

	def __bool__(self):
		return bool(self.text)

	def __str__(self):
		return str(self.text)

	def read(self, indata):
		self.text = indata.get('value')
		self.wide = indata.get('wide')=='true'

class cubasexml_object:
	def __init__(self, indata):
		self.obj_class = None
		self.obj_id = -1
		self.obj_data = {}
		self.ref_obj = None
		self.is_pointer = False
		if indata is not None: self.read(indata)

	def __repr__(self):
		outtxt = ''
		if self.obj_class:
			outtxt += 'Class: "'+str(self.obj_class)+'" '
			outtxt += 'Data: '+str(list(self.obj_data))
			return '<Seq3 Obj - %s>' % outtxt
		else:
			outtxt += 'ID: "'+str(self.obj_id)+'" '
			return '<Seq3 Pointer - %s>' % outtxt

	def __getitem__(self, k):
		return self.obj_data.__getitem__(k)

	def __contains__(self, k):
		return self.obj_data.__contains__(k)

	def read(self, indata):
		attrib = indata.attrib
		if 'class' in attrib: 
			self.obj_class = attrib['class']
		if 'ID' in attrib: 
			self.obj_id = int(attrib['ID'])
			if not self.obj_class: self.is_pointer = True
			if not self.is_pointer: globalstate.globalids[self.obj_id] = self
		for x in iter_xdata(indata):
			if not x[0]: print('unknown tag in obj:', x)
			else: self.obj_data[x[2]] = x[3]

		#if self.obj_id and self.obj_class:
		#	globalstate.debug_alld[self.obj_id] = self
		if self.obj_id and not self.obj_class:
			globalstate.debug_allp[self.obj_id] = self

class cubasexml_list_int:
	def __init__(self, *args): self.data = args[0] if args else []
	def __len__(self): return self.data.__len__()
	def __getitem__(self, i): return self.data.__getitem__(i)
	def __setitem__(self, i, v): return self.data.__setitem__(i, v)
	def setvals(self, x): self.data = x
	def append(self, i): return self.data.append(i)
	def make_xml(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'list')
		if name: tempxml.set('name', name)
		tempxml.set('type', 'int')
		for x in self.data:
			inxml = ET.SubElement(tempxml, 'item')
			inxml.set('value', str(x))

class cubasexml_list_float:
	def __init__(self, *args): self.data = args[0] if args else []
	def __len__(self): return self.data.__len__()
	def __getitem__(self, i): return self.data.__getitem__(i)
	def __setitem__(self, i, v): return self.data.__setitem__(i, v)
	def setvals(self, x): self.data = x
	def append(self, i): return self.data.append(i)
	def make_xml(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'list')
		if name: tempxml.set('name', name)
		tempxml.set('type', 'float')
		for x in self.data:
			inxml = ET.SubElement(tempxml, 'item')
			inxml.set('value', str(x))

class cubasexml_list_string:
	def __init__(self, *args): self.data = args[0] if args else []
	def __len__(self): return self.data.__len__()
	def __getitem__(self, i): return self.data.__getitem__(i)
	def __setitem__(self, i, v): return self.data.__setitem__(i, v)
	def setvals(self, x): self.data = x
	def append(self, i): return self.data.append(i)
	def make_xml(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'list')
		if name: tempxml.set('name', name)
		tempxml.set('type', 'string')
		for x in self.data:
			inxml = ET.SubElement(tempxml, 'item')
			inxml.set('value', x.text)

class cubasexml_list_dict:
	def __init__(self, *args): self.data = args[0] if args else []
	def __len__(self): return self.data.__len__()
	def __getitem__(self, i): return self.data.__getitem__(i)
	def __setitem__(self, i, v): return self.data.__setitem__(i, v)
	def setvals(self, x): self.data = x
	def append(self, i): return self.data.append(i)
	def make_xml(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'list')
		if name: tempxml.set('name', name)
		tempxml.set('type', 'list')
		for x in self.data:
			inxml = ET.SubElement(tempxml, 'item')
			write_xdata(x, inxml)

class cubasexml_list_obj:
	def __init__(self, *args): self.data = args[0] if args else []
	def __len__(self): return self.data.__len__()
	def __getitem__(self, i): return self.data.__getitem__(i)
	def __setitem__(self, i, v): return self.data.__setitem__(i, v)
	def setvals(self, x): self.data = x
	def append(self, i): return self.data.append(i)
	def make_xml(self, xmldata, name):
		tempxml = ET.SubElement(xmldata, 'list')
		if name: tempxml.set('name', name)
		tempxml.set('type', 'obj')
		for x in self.data:
			makeval__obj(tempxml, None, x)

# ================================================ FUNC READ ================================================

def getval__dict(xmldata):
	outdata = {}
	for x in iter_xdata(xmldata):
		if not x[0]: print('unknown tag in member:', x)
		else: outdata[x[2]] = x[3]
	return outdata

def getval__int(x):
	return int(x.get('value'))

def getval__float(x):
	return float(x.get('value'))

def getval__bin(x):
	return bytes.fromhex(x.text) if x.text else b''

def getval__string(x):
	return cubasexml_string(x)

def getval__list(x):
	listtype = x.get('type')
	if listtype=='obj':
		listdata = cubasexml_list_obj()
		for d in x:
			if d.tag=='obj': listdata.append(get_object(cubasexml_object(d)))
	elif listtype=='int':
		listdata = cubasexml_list_int()
		for d in x:
			if d.tag=='item': listdata.append(int(d.get('value')))
	elif listtype=='float':
		listdata = cubasexml_list_float()
		for d in x:
			if d.tag=='item': listdata.append(float(d.get('value')))
	elif listtype=='string':
		listdata = cubasexml_list_string()
		for d in x:
			if d.tag=='item': listdata.append(cubasexml_string(d))
	elif listtype=='list':
		listdata = cubasexml_list_dict()
		for d in x:
			if d.tag=='item':
				itemdata = {}
				for i in iter_xdata(d):
					if not i[0]: print('unknown tag in list/list:', i)
					else: itemdata[i[2]] = i[3]
				listdata.append(itemdata)
	else: exit(('unknown list type %s' % str(listtype)))
	return listdata

def iter_xdata(xdata):
	for x in xdata:
		if x.tag == 'int':	    	yield True, 'int',    x.get('name'), getval__int(x)
		elif x.tag == 'float':		yield True, 'float',  x.get('name'), getval__float(x)
		elif x.tag == 'string':		yield True, 'string', x.get('name'), getval__string(x)
		elif x.tag == 'list':		yield True, 'list',   x.get('name'), getval__list(x)
		elif x.tag == 'obj':		yield True, 'object', x.get('name'), get_object(cubasexml_object(x))
		elif x.tag == 'member':		yield True, 'member', x.get('name'), getval__dict(x)
		elif x.tag == 'bin':		yield True, 'binary', x.get('name'), getval__bin(x)
		else:						yield False, x.tag,   x.attrib

# ================================================ FUNC WRITE ================================================

def makeval__dict(xmldata, name, indata):
	tempxml = ET.SubElement(xmldata, 'member')
	if name: tempxml.set('name', name)
	if indata: write_xdata(indata, tempxml)
	else: tempxml.text = ''

def makeval__int(xmldata, name, val):
	tempxml = ET.SubElement(xmldata, 'int')
	tempxml.set('name', name)
	tempxml.set('value', str(int(val)))

def makeval__float(xmldata, name, val):
	tempxml = ET.SubElement(xmldata, 'float')
	tempxml.set('name', name)
	if not DEBUG_EASY_COMPARE:
		tempxml.set('value', str(val if val%1 else int(val)))

def makeval__bin(xmldata, name, val):
	tempxml = ET.SubElement(xmldata, 'bin')
	tempxml.set('name', name)
	if not DEBUG_EASY_COMPARE:
		if val:
			tempxml.text = '\n'+('\n').join(wrap(binascii.hexlify(val).decode().upper(), 64))
		else:
			tempxml.text = ''

def makeval__string(xmldata, name, val, iswide):
	tempxml = ET.SubElement(xmldata, 'string')
	tempxml.set('name', name)
	if isinstance(val, cubasexml_string):
		tempxml.set('value', val.text)
		if val.wide: tempxml.set('wide', 'true')
	else:
		tempxml.set('value', str(val))
		if iswide: tempxml.set('wide', 'true')

def makeval__obj(xmldata, name, val):
	if type(val) in classesmake:
		tempxml = ET.SubElement(xmldata, 'obj')
		tempxml.set('class', classesmake[type(val)])
		if name: tempxml.set('name', name)
		if not DEBUG_EASY_COMPARE: tempxml.set('ID', str(val.idnum))
		if 'make_xml' in dir(val): val.make_xml(tempxml)
		else: print('make_xml not found in', type(val))
	if isinstance(val, obj_pointer):
		makeval__pointer(xmldata, name, val.idnum)

def makeval__pointer(xmldata, name, idnum):
	tempxml = ET.SubElement(xmldata, 'obj')
	if name: tempxml.set('name', name)
	tempxml.set('ID', str(idnum))

def makeval__list(xmldata, name, val):
	if isinstance(val, cubasexml_list_int):
		val.make_xml(xmldata, name)
	elif isinstance(val, cubasexml_list_float):
		val.make_xml(xmldata, name)
	elif isinstance(val, cubasexml_list_string):
		val.make_xml(xmldata, name)
	elif isinstance(val, cubasexml_list_dict):
		val.make_xml(xmldata, name)
	elif isinstance(val, cubasexml_list_obj):
		val.make_xml(xmldata, name)
	else:
		print('unknown list type', xmldata.attrib, val)

def write_xdata(obj_data, xmldata):
	for k, v in obj_data.items():
		if isinstance(v, dataclasses.Field): v = v.default_factory()
		if isinstance(v, dict): makeval__dict(xmldata, k, v)
		elif isinstance(v, int): makeval__int(xmldata, k, v)
		elif isinstance(v, bytes): makeval__bin(xmldata, k, v)
		elif isinstance(v, float): makeval__float(xmldata, k, v)
		elif isinstance(v, cubasexml_string): makeval__string(xmldata, k, v, 1)
		elif isinstance(v, list): makeval__list(xmldata, k, v)
		elif isinstance(v, obj_pointer): makeval__pointer(xmldata, k, v.idnum)
		elif isinstance(v, cubasexml_list_int): v.make_xml(xmldata, k)
		elif isinstance(v, cubasexml_list_float): v.make_xml(xmldata, k)
		elif isinstance(v, cubasexml_list_string): v.make_xml(xmldata, k)
		elif isinstance(v, cubasexml_list_obj): v.make_xml(xmldata, k)
		elif isinstance(v, cubasexml_list_dict): v.make_xml(xmldata, k)
		elif isinstance(v, seq_domain): makeval__dict(xmldata, k, v.to_dict())
		elif type(v) in classesmake: makeval__obj(xmldata, k, v)
		else:
			print( 'write_xdata', type(v) )

# ================================================ OBJECTS ================================================

classes = {}

def get_object(seqobj):
	if not seqobj.is_pointer:
		if seqobj.obj_class in globalstate.classes: 
			objc = globalstate.classes[seqobj.obj_class]()
			objc.from_seqobj(seqobj)
			globalstate.debug_alld[seqobj.obj_id] = objc
			return objc
		else:
			print('class not found', seqobj.obj_class)
	else:
		objc = obj_pointer()
		objc.from_seqobj(seqobj)
		return objc

class seq_value:
	value: float = 0
	v_min: float = 0
	v_max: float = 1
	def set_vals(self, value, v_min, v_max):
		self.value = value
		self.v_min = v_min
		self.v_max = v_max
	def from_dict(self, memberobj):
		if 'Value' in memberobj: self.value = memberobj['Value']
		if 'Min' in memberobj: self.v_min = memberobj['Min']
		if 'Max' in memberobj: self.v_max = memberobj['Max']
	def to_dict(self):
		return {'Value': int(self.value), 'Min': int(self.v_min), 'Max': int(self.v_max)}

@dataclass
class obj_pointer:
	idnum: int = -1
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id

class seq_domain:
	dtype: int = 0
	tempo_track: obj_pointer = field(default_factory=obj_pointer)
	signature_track: obj_pointer = field(default_factory=obj_pointer)
	period: float = 1
	def from_dict(self, memberobj):
		if 'Type' in memberobj: self.dtype = memberobj['Type']
		if 'Tempo Track' in memberobj: self.tempo_track = memberobj['Tempo Track']
		if 'Signature Track' in memberobj: self.signature_track = memberobj['Signature Track']
		if 'Period' in memberobj: self.period = memberobj['Period']
	def set_sync(self, id_trk_bpm, id_trk_meas):
		self.dtype = 0
		self.tempo_track = obj_pointer()
		self.signature_track = obj_pointer()
		self.tempo_track.idnum = id_trk_bpm
		self.signature_track.idnum = id_trk_meas
	def set_period(self, period):
		self.dtype = 1
		self.period = period
	def to_dict(self):
		if self.dtype == 0:
			return {'Type': int(self.dtype), 'Tempo Track': self.tempo_track, 'Signature Track': self.signature_track}
		elif self.dtype == 1:
			return {'Type': int(self.dtype), 'Period': float(self.period)}
		elif self.dtype == 10:
			return {'Type': int(self.dtype), 'Period': float(self.period)}
		else:
			print('Unknown Domain Type', self.dtype)
			exit()
