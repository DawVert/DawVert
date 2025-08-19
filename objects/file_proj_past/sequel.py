# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from dataclasses import dataclass, field
from lxml import etree as ET
from textwrap import wrap
import binascii

DEBUG_EASY_COMPARE = False

def to_wide_string(textd):
	o = sequel_string(None)
	o.text = textd
	o.wide = True
	return o

def to_norm_string(textd):
	o = sequel_string(None)
	o.text = textd
	return o

# ================================================ FUNC READ ================================================

debug_alld = {}
debug_allp = {}

class sequel_string:
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

class sequel_object:
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
			if not self.is_pointer: globalids[self.obj_id] = self
		for x in iter_xdata(indata):
			if not x[0]: print('unknown tag in obj:', x)
			else: self.obj_data[x[2]] = x[3]

		#if self.obj_id and self.obj_class:
		#	debug_alld[self.obj_id] = self
		if self.obj_id and not self.obj_class:
			debug_allp[self.obj_id] = self

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
	return sequel_string(x)

def getval__list(x):
	listtype = x.get('type')
	listdata = []
	if listtype=='obj':
		for d in x:
			if d.tag=='obj': listdata.append(get_object(sequel_object(d)))
	elif listtype=='int':
		for d in x:
			if d.tag=='item': listdata.append(int(d.get('value')))
	elif listtype=='float':
		for d in x:
			if d.tag=='item': listdata.append(float(d.get('value')))
	elif listtype=='string':
		for d in x:
			if d.tag=='item': listdata.append(sequel_string(d))
	elif listtype=='list':
		for d in x:
			if d.tag=='item':
				itemdata = {}
				for i in iter_xdata(d):
					if not i[0]: print('unknown tag in list/list:', i)
					else: itemdata[i[2]] = i[3]
				listdata.append(itemdata)
	else: exit('unknown list type %s' % str(listtype))
	return listdata

def iter_xdata(xdata):
	for x in xdata:
		if x.tag == 'int':	    	yield True, 'int',    x.get('name'), getval__int(x)
		elif x.tag == 'float':		yield True, 'float',  x.get('name'), getval__float(x)
		elif x.tag == 'string':		yield True, 'string', x.get('name'), getval__string(x)
		elif x.tag == 'list':		yield True, 'list',   x.get('name'), getval__list(x)
		elif x.tag == 'obj':		yield True, 'object', x.get('name'), get_object(sequel_object(x))
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
	if isinstance(val, sequel_string):
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
	tempxml = ET.SubElement(xmldata, 'list')
	tempxml.set('name', name)
	listtypes = [type(x) for x in val]

	if listtypes:
		sametype = all(x == listtypes[0] for x in listtypes)
		if sametype:
			listtype = listtypes[0]
			if listtype == int:
				tempxml.set('type', 'int')
				for x in val:
					inxml = ET.SubElement(tempxml, 'item')
					inxml.set('value', str(x))
			elif listtype == float:
				tempxml.set('type', 'float')
				for x in val:
					inxml = ET.SubElement(tempxml, 'item')
					inxml.set('value', str(x))
			elif listtype == str:
				tempxml.set('type', 'string')
				for x in val:
					inxml = ET.SubElement(tempxml, 'item')
					inxml.set('value', x)
			elif listtype == sequel_string:
				tempxml.set('type', 'string')
				for x in val:
					inxml = ET.SubElement(tempxml, 'item')
					inxml.set('value', x.text)
					if x.wide: inxml.set('wide', 'true')
			elif listtype == dict:
				tempxml.set('type', 'list')
				for x in val:
					inxml = ET.SubElement(tempxml, 'item')
					write_xdata(x, inxml)
			#else:
			#	print('unknown', listtype)
		allobjs = [(x in classesmake) for x in listtypes]
		if all(allobjs):
			tempxml.set('type', 'obj')
			for x in val:
				makeval__obj(tempxml, None, x)

def write_xdata(obj_data, xmldata):
	for k, v in obj_data.items():
		if isinstance(v, dict): makeval__dict(xmldata, k, v)
		elif isinstance(v, int): makeval__int(xmldata, k, v)
		elif isinstance(v, bytes): makeval__bin(xmldata, k, v)
		elif isinstance(v, float): makeval__float(xmldata, k, v)
		elif isinstance(v, sequel_string): makeval__string(xmldata, k, v, 1)
		elif isinstance(v, list): makeval__list(xmldata, k, v)
		elif isinstance(v, obj_pointer): makeval__pointer(xmldata, k, v.idnum)
		elif type(v) in classesmake: makeval__obj(xmldata, k, v)
		else:
			print( type(v) )

# ================================================ OBJECTS ================================================
globalids = {}

classes = {}

def get_object(seqobj):
	if not seqobj.is_pointer:
		if seqobj.obj_class in classes: 
			objc = classes[seqobj.obj_class]()
			objc.from_seqobj(seqobj)
			debug_alld[seqobj.obj_id] = objc
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
	def to_dict(self):
		if self.dtype == 0:
			return {'Type': int(self.dtype), 'Tempo Track': self.tempo_track, 'Signature Track': self.signature_track}
		elif self.dtype == 1:
			return {'Type': int(self.dtype), 'Period': self.period}
		elif self.dtype == 10:
			return {'Type': int(self.dtype), 'Period': self.period}
		else:
			print('Unknown Domain Type', self.dtype)
			exit()

# ================================================ CLASSES ================================================

@dataclass
class class_UTextEditorBuffer:
	idnum: int = 0
	cursor: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Cursor' in obj_data: self.cursor = obj_data['Cursor']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Cursor', self.cursor)
classes['UTextEditorBuffer'] = class_UTextEditorBuffer

@dataclass
class class_ApplicationVersion:
	idnum: int = 0
	application: str = '*Sequel*'
	version: str = 'Version 3.0.0'
	builddate: str = 'Jul 26 2011'
	internalnumber: int = 300
	platform: str = 'WIN32'
	encoding: str = 'UTF-8'
	language: str = 'us'
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Application' in obj_data: self.application = obj_data['Application']
		if 'Version' in obj_data: self.version = obj_data['Version']
		if 'BuildDate' in obj_data: self.builddate = obj_data['BuildDate']
		if 'InternalNumber' in obj_data: self.internalnumber = obj_data['InternalNumber']
		if 'Platform' in obj_data: self.platform = obj_data['Platform']
		if 'Encoding' in obj_data: self.encoding = obj_data['Encoding']
		if 'Language' in obj_data: self.language = obj_data['Language']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Application', self.application, 0)
		makeval__string(xmlobj, 'Version', self.version, 0)
		makeval__string(xmlobj, 'BuildDate', self.builddate, 0)
		makeval__int(xmlobj, 'InternalNumber', self.internalnumber)
		makeval__string(xmlobj, 'Platform', self.platform, 0)
		makeval__string(xmlobj, 'Encoding', self.encoding, 0)
		makeval__string(xmlobj, 'Language', self.language, 0)

classes['Application Version'] = class_ApplicationVersion

@dataclass
class class_UColorSet:
	idnum: int = 0
	setname: str = 'Event Colors'
	c_set: list = field(default_factory=list)
	c_defset: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'SetName' in obj_data: self.setname = obj_data['SetName']
		if 'Set' in obj_data: self.c_set = obj_data['Set']
		if 'DefSet' in obj_data: self.c_defset = obj_data['DefSet']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'SetName', self.setname, 1)
		makeval__list(xmlobj, 'Set', self.c_set)
		makeval__list(xmlobj, 'DefSet', self.c_defset)
classes['UColorSet'] = class_UColorSet

@dataclass
class class_TrackParaEffect:
	idnum: int = 0
	name: str = ''
	index: int = 0
	isinsert: int = 1
	playinstop: int = 0
	inputs: list = field(default_factory=list)
	outputs: list = field(default_factory=list)
	transpose: seq_value = field(default_factory=seq_value)
	velocity_shift: seq_value = field(default_factory=seq_value)
	delay: seq_value = field(default_factory=seq_value)
	length_compression: seq_value = field(default_factory=seq_value)
	velocity_compression: seq_value = field(default_factory=seq_value)
	channelizer: seq_value = field(default_factory=seq_value)
	random1: int = 0
	random2: int = 0
	range1: int = 0
	range2: int = 0
	random1min: int = 0
	random1max: int = 0
	random2min: int = 0
	random2max: int = 0
	range1min: int = 1
	range1max: int = 1
	range2min: int = 1
	range2max: int = 1
	scale: seq_value = field(default_factory=seq_value)
	scale_note: seq_value = field(default_factory=seq_value)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
		if 'Transpose' in obj_data: self.transpose.from_dict(obj_data['Transpose'])
		if 'Velocity Shift' in obj_data: self.velocity_shift.from_dict(obj_data['Velocity Shift'])
		if 'Delay' in obj_data: self.delay.from_dict(obj_data['Delay'])
		if 'Length Compression' in obj_data: self.length_compression.from_dict(obj_data['Length Compression'])
		if 'Velocity Compression' in obj_data: self.velocity_compression.from_dict(obj_data['Velocity Compression'])
		if 'Channelizer' in obj_data: self.channelizer.from_dict(obj_data['Channelizer'])
		if 'Random1' in obj_data: self.random1 = obj_data['Random1']
		if 'Random2' in obj_data: self.random2 = obj_data['Random2']
		if 'Range1' in obj_data: self.range1 = obj_data['Range1']
		if 'Range2' in obj_data: self.range2 = obj_data['Range2']
		if 'Random1Min' in obj_data: self.random1min = obj_data['Random1Min']
		if 'Random1Max' in obj_data: self.random1max = obj_data['Random1Max']
		if 'Random2Min' in obj_data: self.random2min = obj_data['Random2Min']
		if 'Random2Max' in obj_data: self.random2max = obj_data['Random2Max']
		if 'Range1Min' in obj_data: self.range1min = obj_data['Range1Min']
		if 'Range1Max' in obj_data: self.range1max = obj_data['Range1Max']
		if 'Range2Min' in obj_data: self.range2min = obj_data['Range2Min']
		if 'Range2Max' in obj_data: self.range2max = obj_data['Range2Max']
		if 'Scale' in obj_data: self.scale.from_dict(obj_data['Scale'])
		if 'Scale Note' in obj_data: self.scale_note.from_dict(obj_data['Scale Note'])
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 0)
		makeval__int(xmlobj, 'Index', self.index)
		makeval__int(xmlobj, 'IsInsert', self.isinsert)
		makeval__int(xmlobj, 'PlayInStop', self.playinstop)
		makeval__list(xmlobj, 'Inputs', self.inputs)
		makeval__list(xmlobj, 'Outputs', self.outputs)
		makeval__dict(xmlobj, 'Transpose', self.transpose.to_dict())
		makeval__dict(xmlobj, 'Velocity Shift', self.velocity_shift.to_dict())
		makeval__dict(xmlobj, 'Delay', self.delay.to_dict())
		makeval__dict(xmlobj, 'Length Compression', self.length_compression.to_dict())
		makeval__dict(xmlobj, 'Velocity Compression', self.velocity_compression.to_dict())
		makeval__dict(xmlobj, 'Channelizer', self.channelizer.to_dict())
		makeval__int(xmlobj, 'Random1', self.random1)
		makeval__int(xmlobj, 'Random2', self.random2)
		makeval__int(xmlobj, 'Range1', self.range1)
		makeval__int(xmlobj, 'Range2', self.range2)
		makeval__int(xmlobj, 'Random1Min', self.random1min)
		makeval__int(xmlobj, 'Random1Max', self.random1max)
		makeval__int(xmlobj, 'Random2Min', self.random2min)
		makeval__int(xmlobj, 'Random2Max', self.random2max)
		makeval__int(xmlobj, 'Range1Min', self.range1min)
		makeval__int(xmlobj, 'Range1Max', self.range1max)
		makeval__int(xmlobj, 'Range2Min', self.range2min)
		makeval__int(xmlobj, 'Range2Max', self.range2max)
		makeval__dict(xmlobj, 'Scale', self.scale.to_dict())
		makeval__dict(xmlobj, 'Scale Note', self.scale_note.to_dict())
classes['TrackParaEffect'] = class_TrackParaEffect

@dataclass
class class_TControllerLaneDef:
	idnum: int = 0
	height: int = 80
	view_mode: int = 0
	controller: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'View Mode' in obj_data: self.view_mode = obj_data['View Mode']
		if 'Controller' in obj_data: self.controller = obj_data['Controller']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Height', self.height)
		makeval__int(xmlobj, 'View Mode', self.view_mode)
		makeval__int(xmlobj, 'Controller', self.controller)
classes['TControllerLaneDef'] = class_TControllerLaneDef

@dataclass
class class_Segmentation:
	idnum: int = 0
	intervalstartposition: int = 0
	intervalendposition: int = 0
	minimumsegmentlength: int = 0
	numsplitpositions: int = 0
	splitpos: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'intervalStartPosition' in obj_data: self.intervalstartposition = obj_data['intervalStartPosition']
		if 'intervalEndPosition' in obj_data: self.intervalendposition = obj_data['intervalEndPosition']
		if 'minimumSegmentLength' in obj_data: self.minimumsegmentlength = obj_data['minimumSegmentLength']
		if 'numSplitPositions' in obj_data: self.numsplitpositions = obj_data['numSplitPositions']
		for x in range(self.numsplitpositions):
			vstr = 'splitPos'+str(x)
			if vstr in obj_data: self.splitpos[x] = obj_data[vstr]
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'intervalStartPosition', self.intervalstartposition)
		makeval__int(xmlobj, 'intervalEndPosition', self.intervalendposition)
		makeval__int(xmlobj, 'minimumSegmentLength', self.minimumsegmentlength)
		makeval__int(xmlobj, 'numSplitPositions', self.numsplitpositions)
		for x in range(self.numsplitpositions):
			vstr = 'splitPos'+str(x)
			makeval__int(xmlobj, vstr, self.splitpos[x])
classes['Segmentation'] = class_Segmentation

@dataclass
class class_StepEnvelopeGroup:
	idnum: int = 0
	segmentation: class_Segmentation = field(default_factory=class_Segmentation)
	strategy: str = 'HitPoints'
	envelope: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'segmentation' in obj_data: self.segmentation = obj_data['segmentation']
		if 'strategy' in obj_data: self.strategy = obj_data['strategy']
		if 'envelope' in obj_data: self.envelope = obj_data['envelope']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'segmentation', self.segmentation)
		makeval__string(xmlobj, 'strategy', self.strategy, 0)
		makeval__list(xmlobj, 'envelope', self.envelope)
classes['StepEnvelopeGroup'] = class_StepEnvelopeGroup

@dataclass
class class_StepEnvelope:
	idnum: int = 0
	valuetype: str = 'continousRange'
	minvalue: float = 0
	maxvalue: float = 0
	numvalues: int = 0
	values: dict = field(default_factory=dict)
	envelopetype: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'valueType' in obj_data: self.valuetype = obj_data['valueType']
		if 'minValue' in obj_data: self.minvalue = obj_data['minValue']
		if 'maxValue' in obj_data: self.maxvalue = obj_data['maxValue']
		if 'numValues' in obj_data: self.numvalues = obj_data['numValues']
		if 'envelopeType' in obj_data: self.envelopetype = obj_data['envelopeType']
		for x in range(self.numvalues):
			vstr = 'value'+str(x)
			if vstr in obj_data: self.values[x] = obj_data[vstr]
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'valueType', self.valuetype, 0)
		makeval__float(xmlobj, 'minValue', self.minvalue)
		makeval__float(xmlobj, 'maxValue', self.maxvalue)
		makeval__int(xmlobj, 'numValues', self.numvalues)
		for x in range(self.numvalues):
			vstr = 'value'+str(x)
			makeval__float(xmlobj, vstr, self.values[x])
		if self.envelopetype: makeval__string(xmlobj, 'envelopeType', self.envelopetype, 0)
classes['StepEnvelope'] = class_StepEnvelope

@dataclass
class class_SmtgAlgoDescription:
	idnum: int = 0
	precision: int = 3
	grainSize: int = 300
	overlap: float = 0.2
	variance: float = 0.8
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'precision' in obj_data: self.precision = obj_data['precision']
		if 'grainSize' in obj_data: self.grainSize = obj_data['grainSize']
		if 'overlap' in obj_data: self.overlap = obj_data['overlap']
		if 'variance' in obj_data: self.variance = obj_data['variance']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'precision', self.precision)
		makeval__int(xmlobj, 'grainSize', self.grainSize)
		makeval__float(xmlobj, 'overlap', self.overlap)
		makeval__float(xmlobj, 'variance', self.variance)
classes['SmtgAlgoDescription'] = class_SmtgAlgoDescription

@dataclass
class class_ElastiquePreset:
	idnum: int = 0
	processingmode: str = ''
	stereomode: str = ''
	formantpreservation: int = 0
	tapestylemode: int = 0
	pitchaccuratemode: int = 1
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'processingMode' in obj_data: self.processingmode = obj_data['processingMode']
		if 'stereoMode' in obj_data: self.stereomode = obj_data['stereoMode']
		if 'formantPreservation' in obj_data: self.formantpreservation = obj_data['formantPreservation']
		if 'tapeStyleMode' in obj_data: self.tapestylemode = obj_data['tapeStyleMode']
		if 'pitchAccurateMode' in obj_data: self.pitchaccuratemode = obj_data['pitchAccurateMode']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'processingMode', self.processingmode, 0)
		makeval__string(xmlobj, 'stereoMode', self.stereomode, 0)
		makeval__int(xmlobj, 'formantPreservation', self.formantpreservation)
		makeval__int(xmlobj, 'tapeStyleMode', self.tapestylemode)
		makeval__int(xmlobj, 'pitchAccurateMode', self.pitchaccuratemode)
classes['ElastiquePreset'] = class_ElastiquePreset

@dataclass
class class_QCDestinationValue:
	idnum: int = 0
	parametertag: int = -1
	nodepath: str = ''
	originalname: str = ''
	isrelativepath: int = 0
	string: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'ParameterTag' in obj_data: self.parametertag = obj_data['ParameterTag']
		if 'NodePath' in obj_data: self.nodepath = obj_data['NodePath']
		if 'OriginalName' in obj_data: self.originalname = obj_data['OriginalName']
		if 'IsRelativePath' in obj_data: self.isrelativepath = obj_data['IsRelativePath']
		if 'String' in obj_data: self.string = obj_data['String']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'ParameterTag', self.parametertag)
		makeval__string(xmlobj, 'NodePath', self.nodepath, 0)
		makeval__string(xmlobj, 'OriginalName', self.originalname, bool(self.originalname))
		makeval__int(xmlobj, 'IsRelativePath', self.isrelativepath)
		makeval__string(xmlobj, 'String', self.string, 1)
classes['QCDestinationValue'] = class_QCDestinationValue

@dataclass
class class_MMidiNote:
	idnum: int = 0
	start: float = 0
	channel: int = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	length: float = 0
	initial_startoffset: float = 0
	initial_lengthoffset: float = 0
	data3: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Channel' in obj_data: self.channel = obj_data['Channel']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Initial Startoffset' in obj_data: self.initial_startoffset = obj_data['Initial Startoffset']
		if 'Initial Lengthoffset' in obj_data: self.initial_lengthoffset = obj_data['Initial Lengthoffset']
		if 'Data3' in obj_data: self.data3 = obj_data['Data3']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.channel: makeval__int(xmlobj, 'Channel', self.channel)
		makeval__int(xmlobj, 'Data1', self.data1)
		makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Length', self.length)
		if self.initial_startoffset: makeval__float(xmlobj, 'Initial Startoffset', self.initial_startoffset)
		if self.initial_lengthoffset: makeval__float(xmlobj, 'Initial Lengthoffset', self.initial_lengthoffset)
		makeval__int(xmlobj, 'Data3', self.data3)
classes['MMidiNote'] = class_MMidiNote

@dataclass
class class_NoteEvent:
	idnum: int = 0
	ppqposition: float = 0
	muted: int = 0
	pitch: int = 0
	velocity: int = 0
	offvelocity: int = 0
	controllervalue1: int = 0
	controllervalue2: int = 0
	controllervalue3: int = 0
	lengthininternalppq: int = 0
	ppqoffset: int = 0
	offsettoprevious: int = 0
	index: int = 0
	ischord: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'ppqPosition' in obj_data: self.ppqposition = obj_data['ppqPosition']
		if 'muted' in obj_data: self.muted = obj_data['muted']
		if 'pitch' in obj_data: self.pitch = obj_data['pitch']
		if 'velocity' in obj_data: self.velocity = obj_data['velocity']
		if 'offVelocity' in obj_data: self.offvelocity = obj_data['offVelocity']
		if 'controllerValue1' in obj_data: self.controllervalue1 = obj_data['controllerValue1']
		if 'controllerValue2' in obj_data: self.controllervalue2 = obj_data['controllerValue2']
		if 'controllerValue3' in obj_data: self.controllervalue3 = obj_data['controllerValue3']
		if 'lengthInInternalPpq' in obj_data: self.lengthininternalppq = obj_data['lengthInInternalPpq']
		if 'ppqOffset' in obj_data: self.ppqoffset = obj_data['ppqOffset']
		if 'offsetToPrevious' in obj_data: self.offsettoprevious = obj_data['offsetToPrevious']
		if 'index' in obj_data: self.index = obj_data['index']
		if 'isChord' in obj_data: self.ischord = obj_data['isChord']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'ppqPosition', self.ppqposition)
		if self.muted: makeval__int(xmlobj, 'muted', self.muted)
		makeval__int(xmlobj, 'pitch', self.pitch)
		makeval__int(xmlobj, 'velocity', self.velocity)
		makeval__int(xmlobj, 'offVelocity', self.offvelocity)
		makeval__int(xmlobj, 'controllerValue1', self.controllervalue1)
		makeval__int(xmlobj, 'controllerValue2', self.controllervalue2)
		makeval__int(xmlobj, 'controllerValue3', self.controllervalue3)
		makeval__int(xmlobj, 'lengthInInternalPpq', self.lengthininternalppq)
		makeval__int(xmlobj, 'ppqOffset', self.ppqoffset)
		makeval__int(xmlobj, 'offsetToPrevious', self.offsettoprevious)
		makeval__int(xmlobj, 'index', self.index)
		makeval__int(xmlobj, 'isChord', self.ischord)
classes['NoteEvent'] = class_NoteEvent

@dataclass
class class_CmString:
	idnum: int = 0
	s: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 's' in obj_data: self.s = obj_data['s']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 's', self.s, 0)
classes['CmString'] = class_CmString

@dataclass
class class_GTreeEntry:
	idnum: int = 0
	dataobject: int = -1
	flags: int = 0
	name: str = ''
	v_id: int = 0
	subentries: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'DataObject' in obj_data: self.dataobject = obj_data['DataObject'].idnum
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'ID' in obj_data: self.v_id = obj_data['ID']
		if 'SubEntries' in obj_data: self.subentries = obj_data['SubEntries']
	def make_xml(self, xmlobj):
		if self.dataobject != -1: makeval__pointer(xmlobj, 'DataObject', self.dataobject)
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__string(xmlobj, 'Name', self.name, 1)
		if self.subentries: makeval__list(xmlobj, 'SubEntries', self.subentries)
		makeval__int(xmlobj, 'ID', self.v_id)
classes['GTreeEntry'] = class_GTreeEntry

@dataclass
class class_CmLinkedList:
	idnum: int = 0
	ownership: int = 1
	obj: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'ownership' in obj_data: self.ownership = obj_data['ownership']
		if 'obj' in obj_data: self.obj = obj_data['obj']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'ownership', self.ownership)
		if self.obj: makeval__list(xmlobj, 'obj', self.obj)
classes['CmLinkedList'] = class_CmLinkedList

@dataclass
class class_FNPath:
	idnum: int = 0
	name: str = ''
	path: str = ''
	ptype: int = 0
	filetype: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Path' in obj_data: self.path = obj_data['Path']
		if 'Type' in obj_data: self.ptype = obj_data['Type']
		if 'FileType' in obj_data: self.filetype = obj_data['FileType']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__string(xmlobj, 'Path', self.path, 1)
		if self.ptype: makeval__int(xmlobj, 'Type', self.ptype)
		if self.filetype: makeval__dict(xmlobj, 'FileType', self.filetype)
classes['FNPath'] = class_FNPath

@dataclass
class class_CmVariant:
	idnum: int = 0
	type: int = 1
	lvalue: int = 0
	istr: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.type = obj_data['type']
		if 'lValue' in obj_data: self.lvalue = obj_data['lValue']
		if 'str' in obj_data: self.istr = obj_data['str']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.type)
		if self.type == 1: makeval__int(xmlobj, 'lValue', self.lvalue)
		if self.istr: makeval__string(xmlobj, 'str', self.istr, 1)
classes['CmVariant'] = class_CmVariant

@dataclass
class class_PStepData:
	idnum: int = 0
	idx: int = 0
	vel: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Idx' in obj_data: self.idx = obj_data['Idx']
		if 'Vel' in obj_data: self.vel = obj_data['Vel']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Idx', self.idx)
		makeval__int(xmlobj, 'Vel', self.vel)
classes['PStepData'] = class_PStepData

@dataclass
class class_PGridDefinition:
	idnum: int = 0
	tempo: float = 120
	signom: int = 4
	sigdenom: int = 4
	beats: int = 4
	offset: float = 0.0
	offsettempo: float = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Tempo' in obj_data: self.tempo = obj_data['Tempo']
		if 'SigNom' in obj_data: self.signom = obj_data['SigNom']
		if 'SigDenom' in obj_data: self.sigdenom = obj_data['SigDenom']
		if 'Beats' in obj_data: self.beats = obj_data['Beats']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'offsetTempo' in obj_data: self.offsettempo = obj_data['offsetTempo']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Tempo', self.tempo)
		makeval__int(xmlobj, 'SigNom', self.signom)
		makeval__int(xmlobj, 'SigDenom', self.sigdenom)
		makeval__int(xmlobj, 'Beats', self.beats)
		makeval__float(xmlobj, 'Offset', self.offset)
		makeval__float(xmlobj, 'offsetTempo', self.offsettempo)
classes['PGridDefinition'] = class_PGridDefinition

@dataclass
class class_PAudioWarpScale:
	idnum: int = 0
	warptab: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'WarpTab' in obj_data: self.warptab = obj_data['WarpTab']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'WarpTab', self.warptab)
classes['PAudioWarpScale'] = class_PAudioWarpScale

@dataclass
class class_PWarpTab:
	idnum: int = 0
	position: float = 0.0
	warped: float = 0.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Position' in obj_data: self.position = obj_data['Position']
		if 'Warped' in obj_data: self.warped = obj_data['Warped']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Position', self.position)
		makeval__float(xmlobj, 'Warped', self.warped)
classes['PWarpTab'] = class_PWarpTab

@dataclass
class class_AudioCluster:
	idnum: int = 0
	substreams: list = field(default_factory=list)
	segments: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Substreams' in obj_data: self.substreams = obj_data['Substreams']
		if 'Segments' in obj_data: self.segments = obj_data['Segments']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'Substreams', self.substreams)
		makeval__list(xmlobj, 'Segments', self.segments)
classes['AudioCluster'] = class_AudioCluster

@dataclass
class class_AudioFile:
	idnum: int = 0
	fpath: class_FNPath = field(default_factory=class_FNPath)
	speakerarr: dict = field(default_factory=dict)
	framecount: int = 0
	sample_size: int = 0
	frame_size: int = 0
	channels: int = 0
	rate: float = 0
	format: int = 0
	byteorder: int = 0
	dataoffset: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'FPath' in obj_data: self.fpath = obj_data['FPath']
		if 'FrameCount' in obj_data: self.framecount = obj_data['FrameCount']
		if 'Sample Size' in obj_data: self.sample_size = obj_data['Sample Size']
		if 'Frame Size' in obj_data: self.frame_size = obj_data['Frame Size']
		if 'SpeakerArr' in obj_data: self.speakerarr = obj_data['SpeakerArr']
		if 'Channels' in obj_data: self.channels = obj_data['Channels']
		if 'Rate' in obj_data: self.rate = obj_data['Rate']
		if 'Format' in obj_data: self.format = obj_data['Format']
		if 'ByteOrder' in obj_data: self.byteorder = obj_data['ByteOrder']
		if 'DataOffset' in obj_data: self.dataoffset = obj_data['DataOffset']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'FPath', self.fpath)
		makeval__int(xmlobj, 'FrameCount', self.framecount)
		makeval__int(xmlobj, 'Sample Size', self.sample_size)
		makeval__int(xmlobj, 'Frame Size', self.frame_size)
		if self.speakerarr: makeval__dict(xmlobj, 'SpeakerArr', self.speakerarr)
		if self.channels: makeval__int(xmlobj, 'Channels', self.channels)
		makeval__float(xmlobj, 'Rate', self.rate)
		makeval__int(xmlobj, 'Format', self.format)
		makeval__int(xmlobj, 'ByteOrder', self.byteorder)
		makeval__int(xmlobj, 'DataOffset', self.dataoffset)
classes['AudioFile'] = class_AudioFile

@dataclass
class class_MRegionMarker:
	idnum: int = 0
	name: str = ''
	start: float = 0
	length: float = 0
	origin: float = 0
	snap: float = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Origin' in obj_data: self.origin = obj_data['Origin']
		if 'Snap' in obj_data: self.snap = obj_data['Snap']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__float(xmlobj, 'Origin', self.origin)
		makeval__float(xmlobj, 'Snap', self.snap)
classes['MRegionMarker'] = class_MRegionMarker

@dataclass
class class_MHitPointEvent:
	idnum: int = 0
	time: float = 0
	weight: float = 0
	flags: int = 0
	filterflags: int = 0
	peak: float = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Time' in obj_data: self.time = obj_data['Time']
		if 'Weight' in obj_data: self.weight = obj_data['Weight']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'FilterFlags' in obj_data: self.filterflags = obj_data['FilterFlags']
		if 'Peak' in obj_data: self.peak = obj_data['Peak']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Time', self.time)
		makeval__float(xmlobj, 'Weight', self.weight)
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__int(xmlobj, 'FilterFlags', self.filterflags)
		makeval__float(xmlobj, 'Peak', self.peak)
classes['MHitPointEvent'] = class_MHitPointEvent

@dataclass
class class_PAudioClip:
	idnum: int = 0
	name: str = ''
	assetoid: str = ''
	history_number: int = 0
	origin_time: float = 0
	path: class_FNPath = field(default_factory=class_FNPath)
	uid: list = field(default_factory=list)
	additional_attributes: dict = field(default_factory=dict)
	cluster = class_AudioCluster = class_AudioCluster()
	events: list = field(default_factory=list)
	domain: seq_domain = field(default_factory=seq_domain)

	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'AssetOID' in obj_data: self.assetoid = obj_data['AssetOID']
		if 'Cluster' in obj_data: self.cluster = obj_data['Cluster']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
		if 'History Number' in obj_data: self.history_number = obj_data['History Number']
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Origin Time' in obj_data: self.origin_time = obj_data['Origin Time']
		if 'Path' in obj_data: self.path = obj_data['Path']
		if 'UID' in obj_data: self.uid = obj_data['UID']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		if self.events: makeval__list(xmlobj, 'Events', self.events)
		makeval__obj(xmlobj, 'Path', self.path)
		if self.history_number: makeval__int(xmlobj, 'History Number', self.history_number)
		if self.origin_time: makeval__float(xmlobj, 'Origin Time', self.origin_time)
		if self.assetoid: makeval__string(xmlobj, 'AssetOID', self.assetoid, 1)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Cluster', self.cluster)
		if self.uid: makeval__list(xmlobj, 'UID', self.uid)
classes['PAudioClip'] = class_PAudioClip

@dataclass
class class_MParamEvent:
	idnum: int = 0
	start: float = 0
	value: float = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Value' in obj_data: self.value = obj_data['Value']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Value', self.value)
classes['MParamEvent'] = class_MParamEvent

@dataclass
class class_MLinearInterpolator:
	idnum: int = 0
	points: list = field(default_factory=list)
	xmin: float = 0.0
	xmax: float = 1.0
	ymin: float = 0.0
	ymax: float = 1.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Points' in obj_data: self.points = obj_data['Points']
		if 'XMin' in obj_data: self.xmin = obj_data['XMin']
		if 'XMax' in obj_data: self.xmax = obj_data['XMax']
		if 'YMin' in obj_data: self.ymin = obj_data['YMin']
		if 'YMax' in obj_data: self.ymax = obj_data['YMax']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'Points', self.points)
		makeval__float(xmlobj, 'XMin', self.xmin)
		makeval__float(xmlobj, 'XMax', self.xmax)
		makeval__float(xmlobj, 'YMin', self.ymin)
		makeval__float(xmlobj, 'YMax', self.ymax)
classes['MLinearInterpolator'] = class_MLinearInterpolator

@dataclass
class class_MFadeOut:
	idnum: int = 0
	curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Curve' in obj_data: self.curve = obj_data['Curve']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'Curve', self.curve)
classes['MFadeOut'] = class_MFadeOut

@dataclass
class class_MAutomationTrackEvent:
	idnum: int = 0
	flags: int = 0
	start: float = 0
	length: float = 0
	node: obj_pointer = field(default_factory=obj_pointer)
	track_device: obj_pointer = field(default_factory=obj_pointer)
	tag: int = 0
	trackflags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Tag' in obj_data: self.tag = obj_data['Tag']
		if 'TrackFlags' in obj_data: self.trackflags = obj_data['TrackFlags']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		makeval__int(xmlobj, 'Tag', self.tag)
		if self.trackflags: makeval__int(xmlobj, 'TrackFlags', self.trackflags)
classes['MAutomationTrackEvent'] = class_MAutomationTrackEvent

@dataclass
class class_MAutomationNode:
	idnum: int = 0
	name: str = ''
	domain: seq_domain = field(default_factory=seq_domain)
	tracks: list = field(default_factory=list)
	track_device: obj_pointer = field(default_factory=obj_pointer)
	expanded: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Tracks' in obj_data: self.tracks = obj_data['Tracks']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Expanded' in obj_data: self.expanded = obj_data['Expanded']
	def make_xml(self, xmlobj):
		if self.name: makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		if self.tracks: makeval__list(xmlobj, 'Tracks', self.tracks)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		makeval__int(xmlobj, 'Expanded', self.expanded)
classes['MAutomationNode'] = class_MAutomationNode

@dataclass
class class_PTrackIconData:
	idnum: int = 0
	currentimagenamedata: str = ''
	magnifyvaluedata: int = 0
	tintingvaluedata: int = 50
	imagecenterxcoorddata: int = 0
	imagecenterycoorddata: int = 0
	rotatevaluedata: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'currentImageNameData' in obj_data: self.currentimagenamedata = obj_data['currentImageNameData']
		if 'magnifyValueData' in obj_data: self.magnifyvaluedata = obj_data['magnifyValueData']
		if 'tintingValueData' in obj_data: self.tintingvaluedata = obj_data['tintingValueData']
		if 'imageCenterXCoordData' in obj_data: self.imagecenterxcoorddata = obj_data['imageCenterXCoordData']
		if 'imageCenterYCoordData' in obj_data: self.imagecenterycoorddata = obj_data['imageCenterYCoordData']
		if 'rotateValueData' in obj_data: self.rotatevaluedata = obj_data['rotateValueData']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'currentImageNameData', self.currentimagenamedata, 1)
		makeval__int(xmlobj, 'magnifyValueData', self.magnifyvaluedata)
		makeval__int(xmlobj, 'tintingValueData', self.tintingvaluedata)
		makeval__int(xmlobj, 'imageCenterXCoordData', self.imagecenterxcoorddata)
		makeval__int(xmlobj, 'imageCenterYCoordData', self.imagecenterycoorddata)
		makeval__int(xmlobj, 'rotateValueData', self.rotatevaluedata)
classes['PTrackIconData'] = class_PTrackIconData

@dataclass
class class_MPlayRangeListItem:
	idnum: int = 0
	po_event: obj_pointer = field(default_factory=obj_pointer)
	po_event_repeats: int = 1
	po_event_repeats_rational: float = 0.05
	po_event_itemflags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'PO Event' in obj_data: self.po_event = obj_data['PO Event']
		if 'PO Event Repeats' in obj_data: self.po_event_repeats = obj_data['PO Event Repeats']
		if 'PO Event Repeats Rational' in obj_data: self.po_event_repeats_rational = obj_data['PO Event Repeats Rational']
		if 'PO Event ItemFlags' in obj_data: self.po_event_itemflags = obj_data['PO Event ItemFlags']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'PO Event', self.po_event)
		makeval__int(xmlobj, 'PO Event Repeats', self.po_event_repeats)
		makeval__float(xmlobj, 'PO Event Repeats Rational', self.po_event_repeats_rational)
		makeval__int(xmlobj, 'PO Event ItemFlags', self.po_event_itemflags)
classes['MPlayRangeListItem'] = class_MPlayRangeListItem

@dataclass
class class_MAutoFadeSetting:
	idnum: int = 0
	flags: int = 0
	fade_length: float = 0.01
	fadein_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	fadeout_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	crossfade_in_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	crossfade_out_curve: class_MLinearInterpolator = field(default_factory=class_MLinearInterpolator)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Fade Length' in obj_data: self.fade_length = obj_data['Fade Length']
		if 'FadeIn Curve' in obj_data: self.fadein_curve = obj_data['FadeIn Curve']
		if 'FadeOut Curve' in obj_data: self.fadeout_curve = obj_data['FadeOut Curve']
		if 'Crossfade In Curve' in obj_data: self.crossfade_in_curve = obj_data['Crossfade In Curve']
		if 'Crossfade Out Curve' in obj_data: self.crossfade_out_curve = obj_data['Crossfade Out Curve']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Fade Length', self.fade_length)
		makeval__obj(xmlobj, 'FadeIn Curve', self.fadein_curve)
		makeval__obj(xmlobj, 'FadeOut Curve', self.fadeout_curve)
		makeval__obj(xmlobj, 'Crossfade In Curve', self.crossfade_in_curve)
		makeval__obj(xmlobj, 'Crossfade Out Curve', self.crossfade_out_curve)
classes['MAutoFadeSetting'] = class_MAutoFadeSetting

@dataclass
class class_MPlayRangeEvent:
	idnum: int = 0
	flags: int = 0
	start: float = 0
	length: float = 0
	additional_attributes: dict = field(default_factory=dict)
	name: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Name' in obj_data: self.name = obj_data['Name']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__string(xmlobj, 'Name', self.name, 1)

classes['MPlayRangeEvent'] = class_MPlayRangeEvent

@dataclass
class class_MMidiPartEvent:
	idnum: int = 0
	node_idnum: int = -1
	start: float = 0
	length: float = 0
	offset: int = 0
	additional_attributes: dict = field(default_factory=dict)
	z_order: int = 1
	transpose: int = 0
	quantize: obj_pointer = field(default_factory=obj_pointer)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Node' in obj_data: self.node_idnum = obj_data['Node'].idnum
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Z-Order' in obj_data: self.z_order = obj_data['Z-Order']
		if 'Transpose' in obj_data: self.transpose = obj_data['Transpose']
		if 'Quantize' in obj_data: self.quantize = obj_data['Quantize']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		if self.offset: makeval__float(xmlobj, 'Offset', self.offset)
		if self.node_idnum: makeval__pointer(xmlobj, 'Node', self.node_idnum)
		if self.additional_attributes: makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__int(xmlobj, 'Z-Order', self.z_order)
		if self.transpose: makeval__int(xmlobj, 'Transpose', self.transpose)
		makeval__obj(xmlobj, 'Quantize', self.quantize)
classes['MMidiPartEvent'] = class_MMidiPartEvent

@dataclass
class class_MAudioEvent:
	idnum: int = 0
	clip_idnum: int = -1
	start: float = 0
	length: float = 0
	priority: int = 1
	offset: float = 0
	volume: float = 1
	flags: int = 0
	additional_attributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Offset' in obj_data: self.offset = obj_data['Offset']
		if 'Priority' in obj_data: self.priority = obj_data['Priority']
		if 'Volume' in obj_data: self.volume = obj_data['Volume']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'AudioClip' in obj_data: self.clip_idnum = obj_data['AudioClip'].idnum
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		if self.offset: makeval__float(xmlobj, 'Offset', self.offset)
		makeval__int(xmlobj, 'Priority', self.priority)
		if self.volume != 1: makeval__float(xmlobj, 'Volume', self.volume)
		makeval__pointer(xmlobj, 'AudioClip', self.clip_idnum)
		if self.flags: makeval__int(xmlobj, 'Flags', self.flags)
		if self.additional_attributes: makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
classes['MAudioEvent'] = class_MAudioEvent

@dataclass
class class_MListNode:
	idnum: int = 0
	name: str = ''
	domain: seq_domain = field(default_factory=seq_domain)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		if self.events: makeval__list(xmlobj, 'Events', self.events)
classes['MListNode'] = class_MListNode

@dataclass
class class_MAutoListNode:
	idnum: int = 0
	domain: seq_domain = field(default_factory=seq_domain)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
	def make_xml(self, xmlobj):
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		if self.events: makeval__list(xmlobj, 'Events', self.events)
classes['MAutoListNode'] = class_MAutoListNode

@dataclass
class class_MTrack:
	idnum: int = 0
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Connection Type', self.connection_type)
		if self.device_name: makeval__string(xmlobj, 'Device Name', self.device_name, 0)
		if self.channel_id: makeval__int(xmlobj, 'Channel ID', self.channel_id)
		if self.deviceattributes: makeval__dict(xmlobj, 'DeviceAttributes', self.deviceattributes)
classes['MTrack'] = class_MTrack

@dataclass
class class_MDeviceTrackEvent:
	idnum: int = 0
	start: float = 0.0
	length: float = 0
	flags: int = 0
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Automation' in obj_data: self.automation = obj_data['Automation']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		makeval__obj(xmlobj, 'Automation', self.automation)
classes['MDeviceTrackEvent'] = class_MDeviceTrackEvent

@dataclass
class class_MMidiController:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__int(xmlobj, 'Data1', self.data1)
		if self.data2: makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['MMidiController'] = class_MMidiController

@dataclass
class class_MAutomationTrack:
	idnum: int = 0
	connection_type: int = 0
	read: int = 0
	write: int = 0
	device_name: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Read' in obj_data: self.read = obj_data['Read']
		if 'Write' in obj_data: self.write = obj_data['Write']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Connection Type', self.connection_type)
		if self.device_name: makeval__string(xmlobj, 'Device Name', self.device_name, 0)
		makeval__int(xmlobj, 'Read', self.read)
		makeval__int(xmlobj, 'Write', self.write)
classes['MAutomationTrack'] = class_MAutomationTrack

@dataclass
class class_PLaneConfig:
	idnum: int = 0
	swingsetting: int = 1
	slide: float = 0.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'SwingSetting' in obj_data: self.swingsetting = obj_data['SwingSetting']
		if 'Slide' in obj_data: self.slide = obj_data['Slide']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'SwingSetting', self.swingsetting)
		makeval__float(xmlobj, 'Slide', self.slide)
classes['PLaneConfig'] = class_PLaneConfig

@dataclass
class class_CmArray:
	idnum: int = 0
	ownership: int = 1
	obj: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'ownership' in obj_data: self.ownership = obj_data['ownership']
		if 'obj' in obj_data: self.obj = obj_data['obj']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'ownership', self.ownership)
		makeval__list(xmlobj, 'obj', self.obj)
classes['CmArray'] = class_CmArray

@dataclass
class class_MMidiAfterTouch:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.data1: makeval__int(xmlobj, 'Data1', self.data1)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['MMidiAfterTouch'] = class_MMidiAfterTouch

@dataclass
class class_MPlayOrderList:
	idnum: int = 0
	po_listname: str = ''
	po_listitems: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'PO ListName' in obj_data: self.po_listname = obj_data['PO ListName']
		if 'PO ListItems' in obj_data: self.po_listitems = obj_data['PO ListItems']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'PO ListName', self.po_listname, 1)
		if self.po_listitems: makeval__list(xmlobj, 'PO ListItems', self.po_listitems)
classes['MPlayOrderList'] = class_MPlayOrderList

@dataclass
class class_PCollectPort:
	idnum: int = 0
	device: str = ''
	port: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Device' in obj_data: self.device = obj_data['Device']
		if 'Port' in obj_data: self.port = obj_data['Port']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Device', self.device, 1)
		makeval__string(xmlobj, 'Port', self.port, 1)
classes['PCollectPort'] = class_PCollectPort

@dataclass
class class_PExtendedDuplicator:
	idnum: int = 0
	device: str = 'No'
	port: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Device' in obj_data: self.device = obj_data['Device']
		if 'Port' in obj_data: self.port = obj_data['Port']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Device', self.device, 1)
		makeval__string(xmlobj, 'Port', self.port, 1)
classes['PExtendedDuplicator'] = class_PExtendedDuplicator

@dataclass
class class_PQuickControls:
	idnum: int = 0
	numberofquickcontrols: int = 8
	qcdestinations: obj_pointer = field(default_factory=obj_pointer)
	devicenode_name: str = 'Quick Controls'
	classname: str = 'Quick Controls'
	idstring: str = 'Quick Controls'
	nodeflags: int = 0
	numberclassids: int = 2
	classids: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'NumberOfQuickControls' in obj_data: self.numberofquickcontrols = obj_data['NumberOfQuickControls']
		if 'QCDestinations' in obj_data: self.qcdestinations = obj_data['QCDestinations']
		if 'DeviceNode Name' in obj_data: self.devicenode_name = obj_data['DeviceNode Name']
		if 'ClassName' in obj_data: self.classname = obj_data['ClassName']
		if 'IDString' in obj_data: self.idstring = obj_data['IDString']
		if 'NodeFlags' in obj_data: self.nodeflags = obj_data['NodeFlags']
		if 'NumberClassIDs' in obj_data: self.numberclassids = obj_data['NumberClassIDs']
		if 'ClassIDs' in obj_data: self.classids = obj_data['ClassIDs']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'NumberOfQuickControls', self.numberofquickcontrols)
		makeval__obj(xmlobj, 'QCDestinations', self.qcdestinations)
		makeval__string(xmlobj, 'DeviceNode Name', self.devicenode_name, 1)
		makeval__string(xmlobj, 'ClassName', self.classname, 1)
		makeval__string(xmlobj, 'IDString', self.idstring, 1)
		makeval__int(xmlobj, 'NodeFlags', self.nodeflags)
		makeval__int(xmlobj, 'NumberClassIDs', self.numberclassids)
		makeval__list(xmlobj, 'ClassIDs', self.classids)
classes['PQuickControls'] = class_PQuickControls

@dataclass
class class_MGridQuantize:
	idnum: int = 0
	grid: int = 4
	type: int = 0
	swing: float = 0.0
	unquantized: int = 0
	legato: int = 50
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Grid' in obj_data: self.grid = obj_data['Grid']
		if 'Type' in obj_data: self.type = obj_data['Type']
		if 'Swing' in obj_data: self.swing = obj_data['Swing']
		if 'Unquantized' in obj_data: self.unquantized = obj_data['Unquantized']
		if 'Legato' in obj_data: self.legato = obj_data['Legato']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Grid', self.grid)
		makeval__int(xmlobj, 'Type', self.type)
		makeval__float(xmlobj, 'Swing', self.swing)
		makeval__int(xmlobj, 'Unquantized', self.unquantized)
		makeval__int(xmlobj, 'Legato', self.legato)
classes['MGridQuantize'] = class_MGridQuantize

@dataclass
class class_MMidiPitchBend:
	idnum: int = 0
	start: float = 0
	data1: int = 0
	data2: int = 0
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Data1' in obj_data: self.data1 = obj_data['Data1']
		if 'Data2' in obj_data: self.data2 = obj_data['Data2']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		if self.data1: makeval__int(xmlobj, 'Data1', self.data1)
		if self.data2: makeval__int(xmlobj, 'Data2', self.data2)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['MMidiPitchBend'] = class_MMidiPitchBend

@dataclass
class class_MMidiPart:
	idnum: int = 0
	name: str = ''
	domain: seq_domain = field(default_factory=seq_domain)
	events: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Events' in obj_data: self.events = obj_data['Events']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		makeval__list(xmlobj, 'Events', self.events)
classes['MMidiPart'] = class_MMidiPart

@dataclass
class class_MTransposeTrackNode:
	idnum: int = 0
	name: str = ''
	domain: seq_domain = field(default_factory=seq_domain)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
classes['MTransposeTrackNode'] = class_MTransposeTrackNode

@dataclass
class class_MTransposeTrackEvent:
	idnum: int = 0
	flags: int = 0
	start: float = 0.0
	length: float = 0
	node: class_MTransposeTrackNode = field(default_factory=class_MTransposeTrackNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	bound: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'bound' in obj_data: self.bound = obj_data['bound']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		if self.bound: makeval__int(xmlobj, 'bound', self.bound)
classes['MTransposeTrackEvent'] = class_MTransposeTrackEvent

@dataclass
class class_FilterDefaults:
	idnum: int = 0
	categories: list = field(default_factory=list)
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'categories' in obj_data: self.categories = obj_data['categories']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'categories', self.categories)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['FilterDefaults'] = class_FilterDefaults

@dataclass
class class_GTree:
	idnum: int = 0
	root: class_GTreeEntry = field(default_factory=class_GTreeEntry)
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Root' in obj_data: self.root = obj_data['Root']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'Root', self.root)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['GTree'] = class_GTree

@dataclass
class class_MInstrumentTrack:
	idnum: int = 0
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	input_type: int = 0
	input_device_id: str = ''
	input_channel_id: int = 0
	input_port_name: str = ''
	solo_flags: int = 0
	drummapname: str = ''
	bank: int = -0
	patch: int = -0
	presetindex: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes']
		if 'Input Type' in obj_data: self.input_type = obj_data['Input Type']
		if 'Input Device ID' in obj_data: self.input_device_id = obj_data['Input Device ID']
		if 'Input Channel ID' in obj_data: self.input_channel_id = obj_data['Input Channel ID']
		if 'Input Port Name' in obj_data: self.input_port_name = obj_data['Input Port Name']
		if 'Solo Flags' in obj_data: self.solo_flags = obj_data['Solo Flags']
		if 'DrummapName' in obj_data: self.drummapname = obj_data['DrummapName']
		if 'Bank' in obj_data: self.bank = obj_data['Bank']
		if 'Patch' in obj_data: self.patch = obj_data['Patch']
		if 'PresetIndex' in obj_data: self.presetindex = obj_data['PresetIndex']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Connection Type', self.connection_type)
		makeval__string(xmlobj, 'Device Name', self.device_name, 1)
		makeval__int(xmlobj, 'Channel ID', self.channel_id)
		makeval__dict(xmlobj, 'DeviceAttributes', self.deviceattributes)
		makeval__int(xmlobj, 'Input Type', self.input_type)
		makeval__string(xmlobj, 'Input Device ID', self.input_device_id, 0)
		makeval__int(xmlobj, 'Input Channel ID', self.input_channel_id)
		makeval__string(xmlobj, 'Input Port Name', self.input_port_name, 0)
		makeval__int(xmlobj, 'Solo Flags', self.solo_flags)
		if self.drummapname: makeval__string(xmlobj, 'DrummapName', self.drummapname, 1)
		makeval__int(xmlobj, 'Bank', self.bank)
		makeval__int(xmlobj, 'Patch', self.patch)
		makeval__int(xmlobj, 'PresetIndex', self.presetindex)
classes['MInstrumentTrack'] = class_MInstrumentTrack

@dataclass
class class_MInstrumentTrackEvent:
	idnum: int = 0
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MInstrumentTrack = field(default_factory=class_MInstrumentTrack)
	height: int = 0
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'Automation' in obj_data: self.automation = obj_data['Automation']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		if self.height: makeval__int(xmlobj, 'Height', self.height)
		makeval__obj(xmlobj, 'Automation', self.automation)
classes['MInstrumentTrackEvent'] = class_MInstrumentTrackEvent

@dataclass
class class_MAudioTrack:
	idnum: int = 0
	connection_type: int = 0
	device_name: str = ''
	channel_id: int = 0
	deviceattributes: dict = field(default_factory=dict)
	flags: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Connection Type' in obj_data: self.connection_type = obj_data['Connection Type']
		if 'Device Name' in obj_data: self.device_name = obj_data['Device Name']
		if 'Channel ID' in obj_data: self.channel_id = obj_data['Channel ID']
		if 'DeviceAttributes' in obj_data: self.deviceattributes = obj_data['DeviceAttributes']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Connection Type', self.connection_type)
		makeval__string(xmlobj, 'Device Name', self.device_name, 0)
		makeval__int(xmlobj, 'Channel ID', self.channel_id)
		makeval__dict(xmlobj, 'DeviceAttributes', self.deviceattributes)
		makeval__int(xmlobj, 'Flags', self.flags)
classes['MAudioTrack'] = class_MAudioTrack

@dataclass
class class_MAudioTrackEvent:
	idnum: int = 0
	flags: int = 0.0
	start: float = 0.0
	length: float = 1007999.9899864197
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MAudioTrack = field(default_factory=class_MAudioTrack)
	height: int = 0
	automation: class_MAutomationNode = field(default_factory=class_MAutomationNode)
	autofade_settings: class_MAutoFadeSetting = field(default_factory=class_MAutoFadeSetting)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'Height' in obj_data: self.height = obj_data['Height']
		if 'Automation' in obj_data: self.automation = obj_data['Automation']
		if 'Autofade Settings' in obj_data: self.autofade_settings = obj_data['Autofade Settings']
	def make_xml(self, xmlobj):
		if self.flags: makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		if self.height: makeval__int(xmlobj, 'Height', self.height)
		makeval__obj(xmlobj, 'Automation', self.automation)
		makeval__obj(xmlobj, 'Autofade Settings', self.autofade_settings)
classes['MAudioTrackEvent'] = class_MAudioTrackEvent

@dataclass
class class_MPlayRangeTrackEvent:
	idnum: int = 0
	flags: int = 32
	start: float = 0.0
	length: float = 0.0
	node: class_MListNode = field(default_factory=class_MListNode)
	additional_attributes: dict = field(default_factory=dict)
	track_device: class_MTrack = field(default_factory=class_MTrack)
	po_listbase: list = field(default_factory=list)
	po_activelist_index: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Track Device' in obj_data: self.track_device = obj_data['Track Device']
		if 'PO ListBase' in obj_data: self.po_listbase = obj_data['PO ListBase']
		if 'PO ActiveList Index' in obj_data: self.po_activelist_index = obj_data['PO ActiveList Index']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Flags', self.flags)
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Track Device', self.track_device)
		makeval__list(xmlobj, 'PO ListBase', self.po_listbase)
		makeval__int(xmlobj, 'PO ActiveList Index', self.po_activelist_index)
classes['MPlayRangeTrackEvent'] = class_MPlayRangeTrackEvent

@dataclass
class class_MTimeSignatureEvent:
	idnum: int = 0
	bar: int = 0
	numerator: int = 4
	denominator: int = 4
	position: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Bar' in obj_data: self.bar = obj_data['Bar']
		if 'Numerator' in obj_data: self.numerator = obj_data['Numerator']
		if 'Denominator' in obj_data: self.denominator = obj_data['Denominator']
		if 'Position' in obj_data: self.position = obj_data['Position']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'Position', self.position)
		makeval__int(xmlobj, 'Numerator', self.numerator)
		makeval__int(xmlobj, 'Denominator', self.denominator)
		if self.bar: makeval__int(xmlobj, 'Bar', self.bar)
classes['MTimeSignatureEvent'] = class_MTimeSignatureEvent

@dataclass
class class_MSignatureTrackEvent:
	idnum: int = 0
	signatureevent: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'SignatureEvent' in obj_data: self.signatureevent = obj_data['SignatureEvent']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'SignatureEvent', self.signatureevent)
classes['MSignatureTrackEvent'] = class_MSignatureTrackEvent

@dataclass
class class_MTempoEvent:
	idnum: int = 0
	bpm: float = 120.0
	ppq: float = 0.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'BPM' in obj_data: self.bpm = obj_data['BPM']
		if 'PPQ' in obj_data: self.ppq = obj_data['PPQ']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'BPM', self.bpm)
		makeval__float(xmlobj, 'PPQ', self.ppq)
classes['MTempoEvent'] = class_MTempoEvent

@dataclass
class class_MTempoTrackEvent:
	idnum: int = 0
	tempoevent: list = field(default_factory=list)
	rehearsaltempo: float = 120
	rehearsalmode: int = 1
	additional_attributes: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'TempoEvent' in obj_data: self.tempoevent = obj_data['TempoEvent']
		if 'RehearsalTempo' in obj_data: self.rehearsaltempo = obj_data['RehearsalTempo']
		if 'RehearsalMode' in obj_data: self.rehearsalmode = obj_data['RehearsalMode']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'TempoEvent', self.tempoevent)
		makeval__float(xmlobj, 'RehearsalTempo', self.rehearsaltempo)
		makeval__int(xmlobj, 'RehearsalMode', self.rehearsalmode)
		if self.additional_attributes: makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
classes['MTempoTrackEvent'] = class_MTempoTrackEvent

@dataclass
class class_MTrackList:
	idnum: int = 0
	domain: seq_domain = field(default_factory=seq_domain)
	tracks: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Domain' in obj_data: self.domain.from_dict(obj_data['Domain'])
		if 'Tracks' in obj_data: self.tracks = obj_data['Tracks']
	def make_xml(self, xmlobj):
		makeval__dict(xmlobj, 'Domain', self.domain.to_dict())
		makeval__list(xmlobj, 'Tracks', self.tracks)
classes['MTrackList'] = class_MTrackList

@dataclass
class class_PControllerLaneSetup:
	idnum: int = 0
	laneinfo: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'LaneInfo' in obj_data: self.laneinfo = obj_data['LaneInfo']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'LaneInfo', self.laneinfo)
classes['PControllerLaneSetup'] = class_PControllerLaneSetup

@dataclass
class class_PDrumMapPool:
	idnum: int = 0
	drum_map: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Drum Map' in obj_data: self.drum_map = obj_data['Drum Map']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'Drum Map', self.drum_map)
classes['PDrumMapPool'] = class_PDrumMapPool

@dataclass
class class_PDrumMap:
	idnum: int = 0
	name: str = ''
	quantize: list = field(default_factory=list)
	map: list = field(default_factory=list)
	order: list = field(default_factory=list)
	outputdevices: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Quantize' in obj_data: self.quantize = obj_data['Quantize']
		if 'Map' in obj_data: self.map = obj_data['Map']
		if 'Order' in obj_data: self.order = obj_data['Order']
		if 'OutputDevices' in obj_data: self.outputdevices = obj_data['OutputDevices']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__list(xmlobj, 'Quantize', self.quantize)
		makeval__list(xmlobj, 'Map', self.map)
		makeval__list(xmlobj, 'Order', self.order)
		if self.outputdevices: makeval__list(xmlobj, 'OutputDevices', self.outputdevices)
classes['PDrumMap'] = class_PDrumMap

@dataclass
class class_PInsVeloPreset:
	idnum: int = 0
	velocities: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Velocities' in obj_data: self.velocities = obj_data['Velocities']
	def make_xml(self, xmlobj):
		makeval__list(xmlobj, 'Velocities', self.velocities)
classes['PInsVeloPreset'] = class_PInsVeloPreset

@dataclass
class class_PPatternBank:
	idnum: int = 0
	name: str = ''
	activepattern: int = 2
	displayedpattern: int = 0
	lanestyle: int = 0
	lanetopitchmap: list = field(default_factory=list)
	mutestates: dict = field(default_factory=dict)
	solostates: dict = field(default_factory=dict)
	usedpatterns: list = field(default_factory=list)
	patterns: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'ActivePattern' in obj_data: self.activepattern = obj_data['ActivePattern']
		if 'DisplayedPattern' in obj_data: self.displayedpattern = obj_data['DisplayedPattern']
		if 'LaneStyle' in obj_data: self.lanestyle = obj_data['LaneStyle']
		if 'LaneToPitchMap' in obj_data: self.lanetopitchmap = obj_data['LaneToPitchMap']
		if 'MuteStates' in obj_data: self.mutestates = obj_data['MuteStates']
		if 'SoloStates' in obj_data: self.solostates = obj_data['SoloStates']
		if 'UsedPatterns' in obj_data: self.usedpatterns = obj_data['UsedPatterns']
		if 'Patterns' in obj_data: self.patterns = obj_data['Patterns']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__int(xmlobj, 'ActivePattern', self.activepattern)
		makeval__int(xmlobj, 'DisplayedPattern', self.displayedpattern)
		makeval__int(xmlobj, 'LaneStyle', self.lanestyle)
		makeval__list(xmlobj, 'LaneToPitchMap', self.lanetopitchmap)
		makeval__dict(xmlobj, 'MuteStates', self.mutestates)
		makeval__dict(xmlobj, 'SoloStates', self.solostates)
		makeval__list(xmlobj, 'UsedPatterns', self.usedpatterns)
		makeval__list(xmlobj, 'Patterns', self.patterns)
classes['PPatternBank'] = class_PPatternBank

@dataclass
class class_PPattern:
	idnum: int = 0
	nrsteps: int = 16
	stepresolution: int = 120
	swinga: float = 0
	swingb: float = 0
	flampos1: float = 0
	flamvel1: float = 0
	flampos2: float = 0
	flamvel2a: float = 0
	flamvel2b: float = 0
	flampos3: float = 0
	flamvel3a: float = 0
	flamvel3b: float = 0
	flamvel3c: float = 0
	nrlanes: int = 128
	laneconfig: list = field(default_factory=list)
	stepdata: list = field(default_factory=list)
	activesteps: int = 3
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'NrSteps' in obj_data: self.nrsteps = obj_data['NrSteps']
		if 'StepResolution' in obj_data: self.stepresolution = obj_data['StepResolution']
		if 'SwingA' in obj_data: self.swinga = obj_data['SwingA']
		if 'SwingB' in obj_data: self.swingb = obj_data['SwingB']
		if 'FlamPos1' in obj_data: self.flampos1 = obj_data['FlamPos1']
		if 'FlamVel1' in obj_data: self.flamvel1 = obj_data['FlamVel1']
		if 'FlamPos2' in obj_data: self.flampos2 = obj_data['FlamPos2']
		if 'FlamVel2a' in obj_data: self.flamvel2a = obj_data['FlamVel2a']
		if 'FlamVel2b' in obj_data: self.flamvel2b = obj_data['FlamVel2b']
		if 'FlamPos3' in obj_data: self.flampos3 = obj_data['FlamPos3']
		if 'FlamVel3a' in obj_data: self.flamvel3a = obj_data['FlamVel3a']
		if 'FlamVel3b' in obj_data: self.flamvel3b = obj_data['FlamVel3b']
		if 'FlamVel3c' in obj_data: self.flamvel3c = obj_data['FlamVel3c']
		if 'NrLanes' in obj_data: self.nrlanes = obj_data['NrLanes']
		if 'LaneConfig' in obj_data: self.laneconfig = obj_data['LaneConfig']
		if 'StepData' in obj_data: self.stepdata = obj_data['StepData']
		if 'ActiveSteps' in obj_data: self.activesteps = obj_data['ActiveSteps']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'NrSteps', self.nrsteps)
		makeval__int(xmlobj, 'StepResolution', self.stepresolution)
		makeval__float(xmlobj, 'SwingA', self.swinga)
		makeval__float(xmlobj, 'SwingB', self.swingb)
		makeval__float(xmlobj, 'FlamPos1', self.flampos1)
		makeval__float(xmlobj, 'FlamVel1', self.flamvel1)
		makeval__float(xmlobj, 'FlamPos2', self.flampos2)
		makeval__float(xmlobj, 'FlamVel2a', self.flamvel2a)
		makeval__float(xmlobj, 'FlamVel2b', self.flamvel2b)
		makeval__float(xmlobj, 'FlamPos3', self.flampos3)
		makeval__float(xmlobj, 'FlamVel3a', self.flamvel3a)
		makeval__float(xmlobj, 'FlamVel3b', self.flamvel3b)
		makeval__float(xmlobj, 'FlamVel3c', self.flamvel3c)
		makeval__int(xmlobj, 'NrLanes', self.nrlanes)
		makeval__list(xmlobj, 'LaneConfig', self.laneconfig)
		makeval__list(xmlobj, 'StepData', self.stepdata)
		makeval__int(xmlobj, 'ActiveSteps', self.activesteps)
classes['PPattern'] = class_PPattern

@dataclass
class class_PStepDesigner2:
	idnum: int = 0
	name: str = ''
	index: int = 0
	isinsert: int = 0
	playinstop: int = 0
	inputs: list = field(default_factory=list)
	outputs: list = field(default_factory=list)
	patternbank: obj_pointer = field(default_factory=obj_pointer)
	triggermode: int = 1
	loopsendlessly: int = 0
	onlyplayduringpatternlength: int = 1
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
		if 'PatternBank' in obj_data: self.patternbank = obj_data['PatternBank']
		if 'TriggerMode' in obj_data: self.triggermode = obj_data['TriggerMode']
		if 'LoopsEndlessly' in obj_data: self.loopsendlessly = obj_data['LoopsEndlessly']
		if 'OnlyPlayDuringPatternLength' in obj_data: self.onlyplayduringpatternlength = obj_data['OnlyPlayDuringPatternLength']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__int(xmlobj, 'Index', self.index)
		makeval__int(xmlobj, 'IsInsert', self.isinsert)
		makeval__int(xmlobj, 'PlayInStop', self.playinstop)
		makeval__list(xmlobj, 'Inputs', self.inputs)
		makeval__list(xmlobj, 'Outputs', self.outputs)
		makeval__obj(xmlobj, 'PatternBank', self.patternbank)
		makeval__int(xmlobj, 'TriggerMode', self.triggermode)
		makeval__int(xmlobj, 'LoopsEndlessly', self.loopsendlessly)
		makeval__int(xmlobj, 'OnlyPlayDuringPatternLength', self.onlyplayduringpatternlength)
classes['PStepDesigner2'] = class_PStepDesigner2

@dataclass
class class_PPool:
	idnum: int = 0
	media_tree: class_GTree = field(default_factory=class_GTree)
	document_path: class_FNPath = field(default_factory=class_FNPath)
	pool_id: int = 0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Media Tree' in obj_data: self.media_tree = obj_data['Media Tree']
		if 'Document Path' in obj_data: self.document_path = obj_data['Document Path']
		if 'Pool ID' in obj_data: self.pool_id = obj_data['Pool ID']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'Media Tree', self.media_tree)
		if self.document_path.path: makeval__obj(xmlobj, 'Document Path', self.document_path)
		makeval__int(xmlobj, 'Pool ID', self.pool_id)
classes['PPool'] = class_PPool

@dataclass
class class_LastAppliedFileInfo:
	idnum: int = 0
	path: obj_pointer = field(default_factory=obj_pointer)
	filename: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Path' in obj_data: self.path = obj_data['Path']
		if 'FileName' in obj_data: self.filename = obj_data['FileName']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'Path', self.path)
		makeval__string(xmlobj, 'FileName', self.filename, 1)
classes['LastAppliedFileInfo'] = class_LastAppliedFileInfo

@dataclass
class class_PMidiEffectBase:
	idnum: int = 0
	name: str = ''
	index: int = 2
	isinsert: int = 0
	playinstop: int = 0
	inputs: list = field(default_factory=list)
	outputs: list = field(default_factory=list)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__int(xmlobj, 'Index', self.index)
		makeval__int(xmlobj, 'IsInsert', self.isinsert)
		makeval__int(xmlobj, 'PlayInStop', self.playinstop)
		makeval__list(xmlobj, 'Inputs', self.inputs)
		makeval__list(xmlobj, 'Outputs', self.outputs)
classes['PMidiEffectBase'] = class_PMidiEffectBase

@dataclass
class class_Root_of_Engine:
	idnum: int = 0
	start: float = 0.0
	length: float = 0
	node: class_MTrackList = field(default_factory=class_MTrackList)
	additional_attributes: dict = field(default_factory=dict)
	working_directory: class_FNPath = field(default_factory=class_FNPath)
	pool: class_PPool = field(default_factory=class_PPool)
	tempo_track: obj_pointer = field(default_factory=obj_pointer)
	signature_track: obj_pointer = field(default_factory=obj_pointer)
	auto_fade_settings: class_MAutoFadeSetting = field(default_factory=class_MAutoFadeSetting)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Length' in obj_data: self.length = obj_data['Length']
		if 'Node' in obj_data: self.node = obj_data['Node']
		if 'Additional Attributes' in obj_data: self.additional_attributes = obj_data['Additional Attributes']
		if 'Working Directory' in obj_data: self.working_directory = obj_data['Working Directory']
		if 'Pool' in obj_data: self.pool = obj_data['Pool']
		if 'Tempo Track' in obj_data: self.tempo_track = obj_data['Tempo Track']
		if 'Signature Track' in obj_data: self.signature_track = obj_data['Signature Track']
		if 'Auto Fade Settings' in obj_data: self.auto_fade_settings = obj_data['Auto Fade Settings']
	def make_xml(self, xmlobj):
		makeval__float(xmlobj, 'Start', self.start)
		makeval__float(xmlobj, 'Length', self.length)
		makeval__obj(xmlobj, 'Node', self.node)
		makeval__dict(xmlobj, 'Additional Attributes', self.additional_attributes)
		makeval__obj(xmlobj, 'Working Directory', self.working_directory)
		makeval__obj(xmlobj, 'Pool', self.pool)
		makeval__obj(xmlobj, 'Tempo Track', self.tempo_track)
		makeval__obj(xmlobj, 'Signature Track', self.signature_track)
		makeval__obj(xmlobj, 'Auto Fade Settings', self.auto_fade_settings)
classes['Root of Engine'] = class_Root_of_Engine

@dataclass
class class_MTransposeEvent:
	idnum: int = 0
	transpose: int = 0
	start: float = 0.0
	flags: int = 0
	length: float = 0.0
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Transpose' in obj_data: self.transpose = obj_data['Transpose']
		if 'Start' in obj_data: self.start = obj_data['Start']
		if 'Flags' in obj_data: self.flags = obj_data['Flags']
		if 'Length' in obj_data: self.length = obj_data['Length']
classes['MTransposeEvent'] = class_MTransposeEvent

@dataclass
class class_PDuplicator:
	idnum: int = 0
	data: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		self.data = seqobj.obj_data
	def make_xml(self, xmlobj):
		xmlobj.text = ''
classes['PDuplicator'] = class_PDuplicator

@dataclass
class class_MiniSequence:
	idnum: int = 0
	lengthppq: int = 1920
	quantize: int = 120
	numberofnotes: int = 0
	events: list = field(default_factory=list)
	usesExlusivePitch: int = 0
	usesFixedPitch: int = 0
	pitches: list = field(default_factory=list)
	controllerNumbers: list = field(default_factory=list)
	controllerEvents: list = field(default_factory=list)

	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'lengthPPQ' in obj_data: self.lengthppq = obj_data['lengthPPQ']
		if 'quantize' in obj_data: self.quantize = obj_data['quantize']
		if 'numberOfNotes' in obj_data: self.numberofnotes = obj_data['numberOfNotes']
		if 'Events' in obj_data: self.events = obj_data['Events']
		if 'usesExlusivePitch' in obj_data: self.usesExlusivePitch = obj_data['usesExlusivePitch']
		if 'usesFixedPitch' in obj_data: self.usesFixedPitch = obj_data['usesFixedPitch']
		if 'pitches' in obj_data: self.pitches = obj_data['pitches']
		if 'controllerNumbers' in obj_data: self.controllerNumbers = obj_data['controllerNumbers']
		if 'controllerEvents' in obj_data: self.controllerEvents = obj_data['controllerEvents']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'lengthPPQ', self.lengthppq)
		makeval__int(xmlobj, 'quantize', self.quantize)
		makeval__int(xmlobj, 'numberOfNotes', self.numberofnotes)
		makeval__list(xmlobj, 'Events', self.events)
		makeval__int(xmlobj, 'usesExlusivePitch', self.usesExlusivePitch)
		makeval__int(xmlobj, 'usesFixedPitch', self.usesFixedPitch)
		makeval__list(xmlobj, 'pitches', self.pitches)
		makeval__list(xmlobj, 'controllerNumbers', self.controllerNumbers)
		if self.controllerEvents: makeval__list(xmlobj, 'controllerEvents', self.controllerEvents)
classes['MiniSequence'] = class_MiniSequence

@dataclass
class class_Phrasor:
	version: int = 2
	idnum: int = 0
	ARP_SX_Version: int = 5
	Name: str = 'Arpache SX'
	Index: int = 2
	IsInsert: int = 1
	PlayInStop: int = 1
	Inputs: list = field(default_factory=list)
	Outputs: list = field(default_factory=list)
	Phrase: int = 0
	phraseName: dict = field(default_factory=dict)
	phraseInfo1: dict = field(default_factory=dict)
	phraseInfo2: dict = field(default_factory=dict)
	origPhraseLength: int = 1
	phraseKey: int = 0
	playMode: int = 5
	sortMode: int = 1
	arpeggiatorMode: int = 2
	sortByPitch: int = 1
	hold: int = 0
	loop: int = 0
	restart: int = 0
	noteLow: int = 1
	noteHigh: int = 127
	midiChannel: int = 0
	thru: int = 0
	phraseLength: int = 0
	velocityOscType: int = 0
	velocityShift: int = 0
	pitchOscType: int = 0
	density: int = 100
	positionOscType: int = 8
	quantize: int = 120
	velocityOscFrequency: int = 0
	pitchOscFrequency: int = 0
	positionOscFrequency: int = 0
	scaler: float = 1.0
	length: int = 120
	velocityOscTypeIndex: int = 0
	pitchOscTypeIndex: int = 0
	positionOscTypeIndex: int = 0
	playModeIndex: int = 5
	sortModeIndex: int = 1
	quantizeIndexIPS: int = 120
	mod1Target: int = 0
	mod2Target: int = 0
	sourceType: int = 3
	velocitySource: int = 1
	polyphony: int = 0
	velocityFix: int = 100
	transpose: int = 0
	repeats: int = 2
	pitchShift: int = 12
	transposeMode: int = 0
	PresetIndex: int = -1
	oscTypeIndex: int = 0
	quantizeIndex: int = 1
	frequency: int = 1
	amplitude: int = 1
	parameterTag: int = 1
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'ARP SX Version' in obj_data:
			self.ARP_SX_Version = obj_data['ARP SX Version']
			self.version = 3
		if 'Name' in obj_data: self.Name = obj_data['Name']
		if 'Index' in obj_data: self.Index = obj_data['Index']
		if 'IsInsert' in obj_data: self.IsInsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.PlayInStop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.Inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.Outputs = obj_data['Outputs']
		if 'Phrase' in obj_data: self.Phrase = obj_data['Phrase'].idnum
		if 'phraseName' in obj_data: self.phraseName = obj_data['phraseName']
		if 'phraseInfo1' in obj_data: self.phraseInfo1 = obj_data['phraseInfo1']
		if 'phraseInfo2' in obj_data: self.phraseInfo2 = obj_data['phraseInfo2']
		if 'origPhraseLength' in obj_data: self.origPhraseLength = obj_data['origPhraseLength']
		if 'phraseKey' in obj_data: self.phraseKey = obj_data['phraseKey']
		if 'playMode' in obj_data: self.playMode = obj_data['playMode']
		if 'sortMode' in obj_data: self.sortMode = obj_data['sortMode']
		if 'arpeggiatorMode' in obj_data: self.arpeggiatorMode = obj_data['arpeggiatorMode']
		if 'sortByPitch' in obj_data: self.sortByPitch = obj_data['sortByPitch']
		if 'hold' in obj_data: self.hold = obj_data['hold']
		if 'loop' in obj_data: self.loop = obj_data['loop']
		if 'restart' in obj_data: self.restart = obj_data['restart']
		if 'noteLow' in obj_data: self.noteLow = obj_data['noteLow']
		if 'noteHigh' in obj_data: self.noteHigh = obj_data['noteHigh']
		if 'midiChannel' in obj_data: self.midiChannel = obj_data['midiChannel']
		if 'thru' in obj_data: self.thru = obj_data['thru']
		if 'phraseLength' in obj_data: self.phraseLength = obj_data['phraseLength']
		if 'velocityOscType' in obj_data: self.velocityOscType = obj_data['velocityOscType']
		if 'velocityShift' in obj_data: self.velocityShift = obj_data['velocityShift']
		if 'pitchOscType' in obj_data: self.pitchOscType = obj_data['pitchOscType']
		if 'density' in obj_data: self.density = obj_data['density']
		if 'positionOscType' in obj_data: self.positionOscType = obj_data['positionOscType']
		if 'quantize' in obj_data: self.quantize = obj_data['quantize']
		if 'velocityOscFrequency' in obj_data: self.velocityOscFrequency = obj_data['velocityOscFrequency']
		if 'pitchOscFrequency' in obj_data: self.pitchOscFrequency = obj_data['pitchOscFrequency']
		if 'positionOscFrequency' in obj_data: self.positionOscFrequency = obj_data['positionOscFrequency']
		if 'scaler' in obj_data: self.scaler = obj_data['scaler']
		if 'length' in obj_data: self.length = obj_data['length']
		if 'velocityOscTypeIndex' in obj_data: self.velocityOscTypeIndex = obj_data['velocityOscTypeIndex']
		if 'pitchOscTypeIndex' in obj_data: self.pitchOscTypeIndex = obj_data['pitchOscTypeIndex']
		if 'positionOscTypeIndex' in obj_data: self.positionOscTypeIndex = obj_data['positionOscTypeIndex']
		if 'playModeIndex' in obj_data: self.playModeIndex = obj_data['playModeIndex']
		if 'sortModeIndex' in obj_data: self.sortModeIndex = obj_data['sortModeIndex']
		if 'quantizeIndexIPS' in obj_data: self.quantizeIndexIPS = obj_data['quantizeIndexIPS']
		if 'mod1Target' in obj_data: self.mod1Target = obj_data['mod1Target']
		if 'mod2Target' in obj_data: self.mod2Target = obj_data['mod2Target']
		if 'sourceType' in obj_data: self.sourceType = obj_data['sourceType']
		if 'velocitySource' in obj_data: self.velocitySource = obj_data['velocitySource']
		if 'polyphony' in obj_data: self.polyphony = obj_data['polyphony']
		if 'velocityFix' in obj_data: self.velocityFix = obj_data['velocityFix']
		if 'transpose' in obj_data: self.transpose = obj_data['transpose']
		if 'repeats' in obj_data:
			self.repeats = obj_data['repeats']
			self.version = 3
		if 'pitchShift' in obj_data:
			self.pitchShift = obj_data['pitchShift']
			self.version = 3
		if 'transposeMode' in obj_data: self.transposeMode = obj_data['transposeMode']
		if 'PresetIndex' in obj_data: self.PresetIndex = obj_data['PresetIndex']
		if 'oscTypeIndex' in obj_data: self.oscTypeIndex = obj_data['oscTypeIndex']
		if 'quantizeIndex' in obj_data: self.quantizeIndex = obj_data['quantizeIndex']
		if 'frequency' in obj_data: self.frequency = obj_data['frequency']
		if 'amplitude' in obj_data: self.amplitude = obj_data['amplitude']
		if 'parameterTag' in obj_data: self.parameterTag = obj_data['parameterTag']

		if 'octaveRange' in obj_data:
			self.octaveRange = obj_data['octaveRange']
			self.version = 2
		if 'transposeStep' in obj_data:
			self.transposeStep = obj_data['transposeStep']
			self.version = 2
	def make_xml(self, xmlobj):
		if self.version == 3: makeval__int(xmlobj, 'ARP SX Version', self.ARP_SX_Version)
		makeval__string(xmlobj, 'Name', self.Name, 1)
		makeval__int(xmlobj, 'Index', self.Index)
		makeval__int(xmlobj, 'IsInsert', self.IsInsert)
		makeval__int(xmlobj, 'PlayInStop', self.PlayInStop)
		makeval__list(xmlobj, 'Inputs', self.Inputs)
		makeval__list(xmlobj, 'Outputs', self.Outputs)
		makeval__pointer(xmlobj, 'Phrase', self.Phrase)
		makeval__dict(xmlobj, 'phraseName', self.phraseName)
		makeval__dict(xmlobj, 'phraseInfo1', self.phraseInfo1)
		makeval__dict(xmlobj, 'phraseInfo2', self.phraseInfo2)
		makeval__int(xmlobj, 'origPhraseLength', self.origPhraseLength)
		makeval__int(xmlobj, 'phraseKey', self.phraseKey)
		makeval__int(xmlobj, 'playMode', self.playMode)
		makeval__int(xmlobj, 'sortMode', self.sortMode)
		makeval__int(xmlobj, 'arpeggiatorMode', self.arpeggiatorMode)
		makeval__int(xmlobj, 'sortByPitch', self.sortByPitch)
		makeval__int(xmlobj, 'hold', self.hold)
		makeval__int(xmlobj, 'loop', self.loop)
		makeval__int(xmlobj, 'restart', self.restart)
		makeval__int(xmlobj, 'noteLow', self.noteLow)
		makeval__int(xmlobj, 'noteHigh', self.noteHigh)
		makeval__int(xmlobj, 'midiChannel', self.midiChannel)
		makeval__int(xmlobj, 'thru', self.thru)
		makeval__int(xmlobj, 'phraseLength', self.phraseLength)
		makeval__int(xmlobj, 'velocityOscType', self.velocityOscType)
		makeval__int(xmlobj, 'velocityShift', self.velocityShift)
		makeval__int(xmlobj, 'pitchOscType', self.pitchOscType)
		makeval__int(xmlobj, 'density', self.density)
		makeval__int(xmlobj, 'positionOscType', self.positionOscType)
		makeval__int(xmlobj, 'quantize', self.quantize)
		makeval__int(xmlobj, 'velocityOscFrequency', self.velocityOscFrequency)
		makeval__int(xmlobj, 'pitchOscFrequency', self.pitchOscFrequency)
		makeval__int(xmlobj, 'positionOscFrequency', self.positionOscFrequency)
		makeval__float(xmlobj, 'scaler', self.scaler)
		makeval__int(xmlobj, 'length', self.length)
		makeval__int(xmlobj, 'velocityOscTypeIndex', self.velocityOscTypeIndex)
		makeval__int(xmlobj, 'pitchOscTypeIndex', self.pitchOscTypeIndex)
		makeval__int(xmlobj, 'positionOscTypeIndex', self.positionOscTypeIndex)
		makeval__int(xmlobj, 'playModeIndex', self.playModeIndex)
		makeval__int(xmlobj, 'sortModeIndex', self.sortModeIndex)
		makeval__int(xmlobj, 'quantizeIndexIPS', self.quantizeIndexIPS)
		makeval__int(xmlobj, 'mod1Target', self.mod1Target)
		makeval__int(xmlobj, 'mod2Target', self.mod2Target)
		makeval__int(xmlobj, 'sourceType', self.sourceType)
		makeval__int(xmlobj, 'velocitySource', self.velocitySource)
		makeval__int(xmlobj, 'polyphony', self.polyphony)
		makeval__int(xmlobj, 'velocityFix', self.velocityFix)
		makeval__int(xmlobj, 'transpose', self.transpose)
		if self.version == 2:
			makeval__int(xmlobj, 'octaveRange', self.octaveRange)
			makeval__int(xmlobj, 'transposeStep', self.transposeStep)
		if self.version == 3:
			makeval__int(xmlobj, 'repeats', self.repeats)
			makeval__int(xmlobj, 'pitchShift', self.pitchShift)
		makeval__int(xmlobj, 'transposeMode', self.transposeMode)
		makeval__int(xmlobj, 'PresetIndex', self.PresetIndex)
		makeval__int(xmlobj, 'oscTypeIndex', self.oscTypeIndex)
		makeval__int(xmlobj, 'quantizeIndex', self.quantizeIndex)
		makeval__int(xmlobj, 'frequency', self.frequency)
		makeval__int(xmlobj, 'amplitude', self.amplitude)
		makeval__int(xmlobj, 'parameterTag', self.parameterTag)

classes['Phrasor'] = class_Phrasor

@dataclass
class class_ChordProcessor:
	version: int = 2
	idnum: int = 0
	name: str = 'Chorder'
	index: int = 1
	isinsert: int = 1
	playinstop: int = 0
	inputs: list = field(default_factory=list)
	outputs: list = field(default_factory=list)
	chordmask: list = field(default_factory=list)
	channel: int = 0
	chordmode: int = 1
	switchmode: int = 0
	thrumode: int = 0
	thrubutton: int = 0
	variationlimiter: int = 0
	presetname: dict = field(default_factory=dict)
	presetindex: int = -1

	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Name' in obj_data: self.name = obj_data['Name']
		if 'Index' in obj_data: self.index = obj_data['Index']
		if 'IsInsert' in obj_data: self.isinsert = obj_data['IsInsert']
		if 'PlayInStop' in obj_data: self.playinstop = obj_data['PlayInStop']
		if 'Inputs' in obj_data: self.inputs = obj_data['Inputs']
		if 'Outputs' in obj_data: self.outputs = obj_data['Outputs']
		if 'ChordMask' in obj_data: self.chordmask = obj_data['ChordMask']
		if 'Channel' in obj_data: self.channel = obj_data['Channel']
		if 'PlayStyle' in obj_data: 
			self.version = 3
			self.PlayStyle = obj_data['PlayStyle']
		if 'ChordMode' in obj_data: self.chordmode = obj_data['ChordMode']
		if 'ThruMode' in obj_data: self.thrumode = obj_data['ThruMode']
		if 'ThruButton' in obj_data:
			self.version = 3
			self.thrubutton = obj_data['ThruButton']
		if 'VariationLimiter' in obj_data: self.variationlimiter = obj_data['VariationLimiter']
		if 'PresetName' in obj_data: self.presetname = obj_data['PresetName']
		if 'PresetIndex' in obj_data: self.presetindex = obj_data['PresetIndex']
		if 'SwitchMode' in obj_data: self.switchmode = obj_data['SwitchMode']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'Name', self.name, 1)
		makeval__int(xmlobj, 'Index', self.index)
		makeval__int(xmlobj, 'IsInsert', self.isinsert)
		makeval__int(xmlobj, 'PlayInStop', self.playinstop)
		makeval__list(xmlobj, 'Inputs', self.inputs)
		makeval__list(xmlobj, 'Outputs', self.outputs)
		makeval__list(xmlobj, 'ChordMask', self.chordmask)
		makeval__int(xmlobj, 'Channel', self.channel)
		if self.version == 3: makeval__int(xmlobj, 'PlayStyle', self.channel)
		makeval__int(xmlobj, 'ChordMode', self.chordmode)
		if self.version == 2: makeval__int(xmlobj, 'SwitchMode', self.switchmode)
		makeval__int(xmlobj, 'ThruMode', self.thrumode)
		if self.version == 3: makeval__int(xmlobj, 'ThruButton', self.thrubutton)
		makeval__int(xmlobj, 'VariationLimiter', self.variationlimiter)
		makeval__dict(xmlobj, 'PresetName', self.presetname)
		makeval__int(xmlobj, 'PresetIndex', self.presetindex)
classes['ChordProcessor'] = class_ChordProcessor

@dataclass
class class_CmBitSet:
	idnum: int = 0
	data: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		self.data = seqobj.obj_data
	def make_xml(self, xmlobj):
		#makeval__dict(xmlobj, 'Domain', self.data)
		pass
classes['CmBitSet'] = class_CmBitSet

@dataclass
class class_Attributes:
	idnum: int = 0
	data: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		self.data = seqobj.obj_data
	def make_xml(self, xmlobj):
		write_xdata(self.data, xmlobj)
classes['Attributes'] = class_Attributes

@dataclass
class class_PEventReader:
	idnum: int = 0
	data: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		self.data = seqobj.obj_data
	def make_xml(self, xmlobj):
		xmlobj.text = ''
classes['PEventReader'] = class_PEventReader

@dataclass
class class_Project:
	idnum: int = 0
	data_root: class_Root_of_Engine = field(default_factory=class_Root_of_Engine)
	setup: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'Data Root' in obj_data: self.data_root = obj_data['Data Root']
		if 'Setup' in obj_data: self.setup = obj_data['Setup']
	def make_xml(self, xmlobj):
		makeval__obj(xmlobj, 'Data Root', self.data_root)
		makeval__dict(xmlobj, 'Setup', self.setup)
classes['Project'] = class_Project

# ================================================ StMedia CLASSES ================================================

@dataclass
class class_StMedia__PureCategoryFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
classes['StMedia::PureCategoryFilter'] = class_StMedia__PureCategoryFilter

@dataclass
class class_StMedia__MultiAttributeFilter:
	idnum: int = 0
	operator: int = 5
	attributes: dict = field(default_factory=dict)
	searchString: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'operator' in obj_data: self.operator = obj_data['operator']
		if 'attributes' in obj_data: self.attributes = obj_data['attributes']
		if 'searchString' in obj_data: self.searchString = obj_data['searchString']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'operator', self.operator)
		makeval__dict(xmlobj, 'attributes', self.attributes)
		makeval__string(xmlobj, 'searchString', self.searchString, 1)
classes['StMedia::MultiAttributeFilter'] = class_StMedia__MultiAttributeFilter

@dataclass
class class_StMedia__CategoryFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
classes['StMedia::CategoryFilter'] = class_StMedia__CategoryFilter

@dataclass
class class_StMedia__RatingFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
classes['StMedia::RatingFilter'] = class_StMedia__RatingFilter

@dataclass
class class_StMedia__TypeFilter:
	idnum: int = 0
	types: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'types' in obj_data: self.types = obj_data['types']
	def make_xml(self, xmlobj):
		makeval__dict(xmlobj, 'types', self.types)
classes['StMedia::TypeFilter'] = class_StMedia__TypeFilter

@dataclass
class class_StMedia__ExtraMultiAttributeFilter:
	idnum: int = 0
	operator: int = 9
	attributes: dict = field(default_factory=dict)
	searchString: str = ''
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'operator' in obj_data: self.operator = obj_data['operator']
		if 'attributes' in obj_data: self.attributes = obj_data['attributes']
		if 'searchString' in obj_data: self.searchString = obj_data['searchString']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'operator', self.operator)
		makeval__dict(xmlobj, 'attributes', self.attributes)
		makeval__string(xmlobj, 'searchString', self.searchString, 1)
classes['StMedia::ExtraMultiAttributeFilter'] = class_StMedia__ExtraMultiAttributeFilter

@dataclass
class class_StMedia__ValueListFilter:
	idnum: int = 0
	attribId: str = ''
	op: int = 0
	values: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'attribId' in obj_data: self.attribId = obj_data['attribId']
		if 'op' in obj_data: self.op = obj_data['op']
		if 'values' in obj_data: self.values = obj_data['values']
	def make_xml(self, xmlobj):
		makeval__string(xmlobj, 'attribId', self.attribId, 0)
		makeval__int(xmlobj, 'op', self.op)
		makeval__dict(xmlobj, 'values', self.values)
classes['StMedia::ValueListFilter'] = class_StMedia__ValueListFilter

@dataclass
class class_StMedia__ValueMatrixFilter:
	idnum: int = 0
	ctype: int = 0
	filters: dict = field(default_factory=dict)
	def from_seqobj(self, seqobj):
		self.idnum = seqobj.obj_id
		obj_data = seqobj.obj_data
		if 'type' in obj_data: self.ctype = obj_data['type']
		if 'filters' in obj_data: self.filters = obj_data['filters']
	def make_xml(self, xmlobj):
		makeval__int(xmlobj, 'type', self.ctype)
		makeval__dict(xmlobj, 'filters', self.filters)
classes['StMedia::ValueMatrixFilter'] = class_StMedia__ValueMatrixFilter

# ================================================ MAIN ================================================

classesmake = dict([(x[1], x[0]) for x in classes.items()])

def indent(elem, level=0):
	# Add indentation
	indent_size = "    "
	i = "\n" + level * indent_size
	if elem.tag=='bin': 
		if elem.text is not None:
			elem.text = elem.text.replace('\n', "\n"+(level+1)*indent_size)
			elem.text += i
		else:
			elem.text += i
	elif elem.tag=='obj': 
		if elem.text is not None:
			elem.text += i
	elif elem.tag=='member': 
		if elem.text is not None:
			elem.text += i
	if len(elem):
		if not elem.text or not elem.text.strip(): elem.text = i + indent_size
		if not elem.tail or not elem.tail.strip(): elem.tail = i
		for elem in elem: indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip(): elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()): elem.tail = i

class sequel_project:
	def __init__(self):
		self.root_objects = {}
		self.def_root_objects = {}
		self.objects = {}

		self.obj_version = None
		self.obj_project = None
		self.obj_devices = None
		self.obj_guistate = None

	def load_from_file(self, filename):
		global globalids
		global debug_alld
		global debug_allp

		self.__init__()
		parser = ET.XMLParser(recover=True)
		tree = ET.parse(filename, parser=parser)

		x_root = tree.getroot()
		debug_alld = {}
		debug_allp = {}
		globalids = {}
		self.def_root_objects = {}
		for x in x_root:
			if x.tag == 'rootObjects':
				for i in x:
					self.def_root_objects[i.get('name')] = int(i.get('ID'))
			else:
				sobj = sequel_object(x)
				self.objects[sobj.obj_id] = get_object(sobj)

		if 'Version' in self.def_root_objects:
			self.obj_version = self.objects[self.def_root_objects['Version']]
		if 'Project' in self.def_root_objects: 
			self.obj_project = self.objects[self.def_root_objects['Project']]
		if 'Devices' in self.def_root_objects:
			self.obj_devices = self.objects[self.def_root_objects['Devices']]
		if 'GuiState' in self.def_root_objects: 
			self.obj_guistate = self.objects[self.def_root_objects['GuiState']]

		if DEBUG_EASY_COMPARE:
			for x in tree.findall(".//*[@class]"):
				if x.get('ID'):
					x.attrib.pop("ID", None)
			for x in tree.findall(".//float"):
				if x.get('value'):
					x.attrib.pop("value", None)
			for x in tree.findall(".//bin"):
				x.text = None
			ET.indent(tree)
			tree.write('outtest.xml', xml_declaration = True)

		return True

	def save_to_file(self, out_file):
		seq_proj = ET.Element("SteinbergProject")
		rootObjects = ET.SubElement(seq_proj, "rootObjects")
		for k, v in self.def_root_objects.items():
			rootx = ET.SubElement(rootObjects, "root")
			rootx.set('name', k)
			rootx.set('ID', str(v))

		for i, o in self.objects.items():
			makeval__obj(seq_proj, None, o)

		indent(seq_proj)
		outfile = ET.ElementTree(seq_proj)
		#ET.indent(outfile)
		outfile.write(out_file, xml_declaration = True, encoding="utf-8")

	def initalize(self):
		self.def_root_objects['Version'] = -1
		self.def_root_objects['Project'] = -1
		self.def_root_objects['Devices'] = -1
		self.def_root_objects['GuiState'] = -1

	def fsck_file(self, filename):
		self.load_from_file(filename)
		for x in debug_allp:
			if x not in debug_alld:
				print('Pointer Target not found', x)
				exit()