# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later
import os
from functions import data_values
from functions import xtramath
import xml.etree.ElementTree as ET

def make_color_text(color):
	return ('#'+'%02x%02x%02x' % (color[0], color[1], color[2]))

def text_to_color(color):
	if '#' in color:
		nonumsign = color.lstrip('#')
		return list(int(nonumsign[i:i+2], 16) for i in (0, 2, 4))
	else:
		return [round(float(x), 7) for x in color.split('|')]			

class datapack_visual:
	__slots__ = ['name', 'color']

	def __init__(self, i_visual):
		self.color = None
		self.name = None
		if i_visual: self.read(i_visual)

	def is_used(self):
		return self.name != None or self.color != None

	def read_xml(self, x_part):
		self.name = x_part.get('name')
		color = x_part.get('color')
		if color: self.color = text_to_color(color)

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'visual')
		if self.name: tempxml.set('name', self.name)
		if self.color: tempxml.set('color', make_color_text(self.color))

	def apply_cvpj_visual(self, visual_obj):
		if self.name: visual_obj.name = self.name
		if self.color: visual_obj.color.set_int(self.color)

class datapack_objectset:
	__slots__ = ['data', 'used', 'in_obj']
	def __init__(self, in_obj):
		self.data = {}
		self.used = False
		self.in_obj = in_obj
	def list(self): 
		return data_values.list__fancysort([x for x in self.data])
	def setused(self): self.used = True
	def create(self, p_name): 
		self.setused()
		self.data[p_name] = self.in_obj(None) if self.in_obj else None
		return self.data[p_name]
	def adddef(self, p_name):
		if p_name not in self.data:
			self.setused()
			self.data[p_name] = self.in_obj(None) if self.in_obj else None
		return self.data[p_name]
	def remove(self, p_name): 
		if p_name in self.data: del self.data[p_name]
	def get(self, p_name): 
		return self.data[p_name] if p_name in self.data else None
	def __iter__(self): 
		for d in self.data.__iter__(): yield d
	def iter(self): 
		for n, d in self.data.items(): yield n, d
	def write_xml(self, xml_data, objname):
		for name, paramd in self.data.items(): 
			tempxml = ET.SubElement(xml_data, objname)
			tempxml.set('id', name)
			paramd.write_xml(tempxml)

class datapack_param_extplug_assoc:
	__slots__ = ['name','num']
	def __init__(self, i_param):
		self.name = ''
		self.num = -1
		if i_param:
			if 'name' in i_param: self.name = i_param['name']
			if 'num' in i_param: self.num = i_param['num']
	def write_xml(self, xml_data):
		if self.name: xml_data.set('name', self.name)
		if self.num != -1: xml_data.set('num', str(self.num))

class datapack_param_onemath:
	__slots__ = ['type','val']
	def __init__(self, i_param):
		self.type = 'lin'
		self.val = 1
		if i_param: self.read(i_param)
	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'type' in attrib: self.type = attrib['type']
		if 'val' in attrib: self.val = float(attrib['val'])
	def is_used(self):
		return self.val != 1 or self.type != 'lin'
	def write_xml(self, xml_data):
		if self.type != 'lin': xml_data.set('type', self.type)
		if self.val != 1: xml_data.set('val', str(self.val))

class datapack_enum_def:
	def __init__(self, xml_data):
		self.enum_max = 0
		self.parts = []
		self.end_point = None

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'enum_max' in attrib: self.enum_max = int(attrib['enum_max'])
		if 'end_point' in attrib: self.end_point = attrib['end_point']
		for inpart in xml_data:
			part_obj = datapack_enum_part()
			part_obj.read_xml(inpart)
			self.parts.append(part_obj)

	def write_xml(self, xml_data):
		xml_data.set('enum_max', str(self.enum_max))
		if self.end_point: xml_data.set('end_point', self.end_point)
		for part in self.parts:
			tempxml = ET.SubElement(xml_data, 'part')
			part.write_xml(tempxml)

class datapack_enum_param:
	def __init__(self, xml_data):
		self.enum_max = 0
		self.parts = []
		self.source = None
		self.end_point = None
		if xml_data != None: self.read_xml(xml_data)

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'enum_max' in attrib: self.enum_max = int(attrib['enum_max'])
		if 'source' in attrib: self.source = attrib['source']
		if 'end_point' in attrib: self.end_point = attrib['end_point']
		for inpart in xml_data:
			part_obj = datapack_enum_part()
			part_obj.read_xml(inpart)
			self.parts.append(part_obj)

	def write_xml(self, xml_data):
		if self.source: xml_data.set('source', str(self.source))
		else: xml_data.set('enum_max', str(self.enum_max))
		if self.end_point: xml_data.set('end_point', self.end_point)
		for part in self.parts:
			tempxml = ET.SubElement(xml_data, 'part')
			part.write_xml(tempxml)

class datapack_enum_part:
	def __init__(self):
		self.num = 0
		self.id = ''
		self.string = ''
		self.name = ''

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'num' in attrib: self.num = int(attrib['num'])
		if 'id' in attrib: self.id = attrib['id']
		if 'string' in attrib: self.string = attrib['string']
		if 'name' in attrib: self.name = attrib['name']

	def write_xml(self, xml_data):
		xml_data.set('num', str(self.num))
		if self.string: xml_data.set('string', str(self.string))
		xml_data.set('id', str(self.id))
		if self.name: xml_data.set('name', str(self.name))

class datapack_param_custom_unit:
	def __init__(self):
		self.out_unit = ""
		self.type = ""
		self.range_in = None
		self.range_out = None
		self.pval = None

	def read_xml(self, xml_data, param_obj):
		attrib = xml_data.attrib
		if 'out_unit' in attrib: self.out_unit = attrib['out_unit']
		if 'type' in attrib: self.type = attrib['type']
		if 'value' in attrib: self.pval = float(attrib['value'])
		if 'range_in' in attrib:
			self.range_in = [float(x) for x in attrib['range_in'].split(':')]
			if len(self.range_in)==1: self.range_in = [0]+self.range_in
		if 'range_out' in attrib:
			self.range_out = [float(x) for x in attrib['range_out'].split(':')]
			if len(self.range_out)==1: self.range_out = [0]+self.range_out
		if self.type=='to_one' and self.range_in == None: self.range_in = [param_obj.min, param_obj.max]

	def write_xml(self, xml_data):
		if self.out_unit: xml_data.set('out_unit', str(self.out_unit))
		xml_data.set('type', str(self.type))
		if self.pval: xml_data.set('value', str(self.pval))
		if self.range_in: xml_data.set('range_in', ':'.join([str(x) for x in self.range_in]))
		if self.range_out: xml_data.set('range_out', ':'.join([str(x) for x in self.range_out]))

class datapack_param:
	#__slots__ = ['type','defv','min','max','name','num','math_zeroone','extplug_assoc','extplug_paramid','unit']

	def __init__(self, i_param):
		self.type = 'none'
		self.defv = 0
		self.defe = None
		self.min = 0
		self.max = 1
		self.name = ''
		self.num = -1
		self.extplug_paramid = None
		self.extplug_assoc = None
		self.math_zeroone = datapack_param_onemath(None)
		self.unit = None
		self.unit_custom = None

		self.is_enum = False
		self.enum_data = None
		if i_param: self.load_dict(i_param)

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		#print(attrib)
		ptype = xml_data.tag
		self.type = ptype
		if 'name' in attrib: self.name = attrib['name']
		if 'num' in attrib: self.num = int(attrib['num'])
		if ptype.startswith('enum'):
			self.is_enum = True
			self.enum_data = datapack_enum_param(xml_data)
			if 'def' in attrib: self.defe = attrib['def']
		else:
			if ptype == 'int':
				if 'def' in attrib: self.defv = int(float(attrib['def']))
				if 'min' in attrib: self.min = int(float(attrib['min']))
				if 'max' in attrib: self.max = int(float(attrib['max']))
			if ptype == 'float':
				if 'def' in attrib: self.defv = float(attrib['def'])
				if 'min' in attrib: self.min = float(attrib['min'])
				if 'max' in attrib: self.max = float(attrib['max'])
			if ptype == 'bool':
				if 'def' in attrib: self.defv = bool(int(attrib['def']))
			if ptype == 'string':
				if 'def' in attrib: self.defv = attrib['def']

		if 'ext_id' in attrib: self.extplug_paramid = attrib['ext_id']
		if 'unit' in attrib: self.unit = attrib['unit']

		for x_part in xml_data:
			if x_part.tag == 'extplug_assoc':
				partattrib = x_part.attrib
				extplug_assoc_obj = datapack_param_extplug_assoc(None)
				if 'name' in partattrib: extplug_assoc_obj.name = partattrib['name']
				if 'num' in partattrib: extplug_assoc_obj.num = int(partattrib['num'])
				if self.extplug_assoc is None: self.extplug_assoc = {}
				self.extplug_assoc[partattrib['type']] = extplug_assoc_obj
			elif x_part.tag == 'math_zeroone':
				partattrib = x_part.attrib
				math_zeroone_obj = self.math_zeroone
				if 'type' in partattrib: math_zeroone_obj.type = partattrib['type']
				if 'val' in partattrib: math_zeroone_obj.val = float(partattrib['val'])

	def get_def_one(self):
		return xtramath.between_to_one(self.min, self.max, self.defv)

	def get_extplug_info(self, exttype):
		outname = self.name
		outnum = self.num

		if self.extplug_assoc:
			if exttype in self.extplug_assoc:
				extdata = self.extplug_assoc[exttype]
				if extdata.name: outname = extdata.name
				if extdata.num != -1: outnum = extdata.num
				if extdata.num < -1: outnum = -1

		return outnum, outname

	def write_xml(self, xml_data):
		xml_data.tag = self.type
		if self.num not in [-1, None]: 
			idd = xml_data.attrib['id']
			xml_data.attrib = {}
			xml_data.set('num', str(self.num))
			xml_data.set('id', idd)
		if self.name: xml_data.set('name', str(self.name))

		if not self.is_enum:
			if self.defv not in [0, None]: 
				if self.type=='string': xml_data.set('def', str(self.defv))
				elif self.type=='bool': xml_data.set('def', "%g" % int(self.defv))
				elif self.type=='float': xml_data.set('def', "%g" % round(self.defv, 7))
				elif self.type=='list': pass
				else: xml_data.set('def', str(self.defv))
			if self.max not in [1, None]: xml_data.set('max', "%g" % round(self.max, 7))
			if self.min not in [0, None]: xml_data.set('min', "%g" % round(self.min, 7))
		else:
			if self.defe: xml_data.set('def', str(self.defe))
			self.enum_data.write_xml(xml_data)

		if self.extplug_paramid != None: xml_data.set('ext_id', str(self.extplug_paramid))
		if self.math_zeroone.is_used(): 
			tempxml = ET.SubElement(xml_data, 'math_zeroone')
			self.math_zeroone.write_xml(tempxml)
		if self.extplug_assoc != None: 
			for k, v in self.extplug_assoc.items(): 
				tempxml = ET.SubElement(xml_data, 'extplug_assoc')
				tempxml.set('type', k)
				v.write_xml(tempxml)
		if self.unit !=  None: xml_data.set('unit', self.unit)

class datapack_drum:
	__slots__ = ['visual']
	def __init__(self, i_drum):
		self.visual = datapack_visual(i_drum['visual'] if 'visual' in i_drum else None) if i_drum else datapack_visual(None)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'visual': self.visual.read_xml(x_part)

	def write_xml(self, xml_data):
		self.visual.write_xml(xml_data)

class datapack_colorset:
	__slots__ = ['value']
	def __init__(self, indata):
		self.value = indata

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		self.value = []
		for x_part in xml_data:
			if x_part.tag == 'color':
				self.value.append(text_to_color(x_part.text))

	def write_xml(self, xml_data):
		for color in self.value:
			tempxml = ET.SubElement(xml_data, 'color')
			tempxml.text = make_color_text(color)

class datapack_datadef:
	__slots__ = ['path', 'name', 'struct']
	def __init__(self):
		self.path = None
		self.name = None
		self.struct = None

	def is_used(self): return self.path or self.name or self.struct

	def read_xml(self, xml_data):
		self.path = xml_data.get('path')
		self.name = xml_data.get('name')
		self.struct = xml_data.get('struct')

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'datadef')
		if self.path is not None: tempxml.set('path',str(self.path))
		if self.name is not None: tempxml.set('name',str(self.name))
		if self.struct is not None: tempxml.set('struct',str(self.struct))

class datapack_datapack_ext:
	__slots__ = ['id', 'category', 'object']
	def __init__(self):
		self.id = None
		self.category = None
		self.object = None

	def is_used(self): return self.id or self.category or self.object

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		if 'id' in attrib: self.id = attrib['id']
		if 'category' in attrib: self.category = attrib['category']
		if 'object' in attrib: self.object = attrib['object']

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'datapack_ext')
		if self.id: tempxml.set('id', self.id)
		if self.category: tempxml.set('category', self.category)
		if self.object: tempxml.set('object', self.object)


class datapack_midi:
	__slots__ = ['used', 'bank', 'bank_hi', 'is_drum', 'patch', 'transpose']
	def __init__(self):
		self.used = False
		self.bank = 0
		self.bank_hi = 0
		self.is_drum = False
		self.patch = 0
		self.transpose = 0

	def read_xml(self, xml_data):
		attrib = xml_data.attrib
		self.used = True
		if 'bank' in attrib: self.bank = int(attrib['bank'])
		if 'bank_hi' in attrib: self.bank_hi = int(attrib['bank_hi'])
		if 'is_drum' in attrib: self.is_drum = attrib['is_drum']=='1'
		if 'patch' in attrib: self.patch = int(attrib['patch'])
		if 'transpose' in attrib: self.transpose = int(attrib['transpose'])

	def write_xml(self, xml_data):
		tempxml = ET.SubElement(xml_data, 'midi')
		if self.bank is not None:
			if self.bank: tempxml.set('bank',str(self.bank))
		if self.bank_hi is not None:
			if self.bank_hi: tempxml.set('bank_hi',str(self.bank_hi))
		if self.is_drum is not None:
			if self.is_drum: tempxml.set('is_drum',str(int(self.is_drum)))
		if self.patch is not None:
			if self.patch: tempxml.set('patch',str(self.patch))
		if self.transpose is not None:
			if self.transpose: tempxml.set('transpose',str(self.transpose))


class datapack_object_extplug_assoc:
	#__slots__ = ['vst2_id', 'vst3_id', 'clap_id', 'vst2_name', 'vst3_name', 'clap_name', 'used']
	def __init__(self):
		self.used = False
		self.vst2 = {}
		self.vst3 = {}
		self.clap = {}

	def read_xml(self, xml_data):
		self.used = True
		for inpart in xml_data: 
			plugtype = inpart.tag
			for ininpart in inpart:
				plugid = int(ininpart.get('plug'))
				cvpjid = ininpart.get('id')
				if plugtype=='vst2': self.vst2[cvpjid] = plugid
				if plugtype=='vst3': self.vst3[cvpjid] = plugid
				if plugtype=='clap': self.clap[cvpjid] = plugid
#
	def write_xml(self, xml_data):
		if self.vst2:
			tempxml = ET.SubElement(xml_data, 'vst2')
			for k,v in self.vst2.items():
				paramxml = ET.SubElement(tempxml, 'param')
				paramxml.set('plug', str(v))
				paramxml.set('id', k)
		if self.vst3:
			tempxml = ET.SubElement(xml_data, 'vst3')
			for k,v in self.vst3.items():
				paramxml = ET.SubElement(tempxml, 'param')
				paramxml.set('plug', str(v))
				paramxml.set('id', k)
		if self.clap:
			tempxml = ET.SubElement(xml_data, 'clap')
			for k,v in self.clap.items():
				paramxml = ET.SubElement(tempxml, 'param')
				paramxml.set('plug', str(v))
				paramxml.set('id', k)

class datapack_object:
	__slots__ = ['visual', 'data', 'enums', 'params', 'datavals', 'drumset', 'datadef', 'datapack_ext', 'midi', 'extplug_assoc']
	def __init__(self, i_object):
		self.visual = datapack_visual(None)
		self.data = {}
		self.enums = datapack_objectset(datapack_enum_def)
		self.params = datapack_objectset(datapack_param)
		self.datavals = datapack_objectset(datapack_param)
		self.drumset = datapack_objectset(datapack_drum)
		self.datadef = datapack_datadef()
		self.datapack_ext = datapack_datapack_ext()
		self.midi = datapack_midi()
		self.extplug_assoc = datapack_object_extplug_assoc()
		if i_object: self.load_dict(i_object)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'enums':
				for inpart in x_part:
					cat_id = inpart.get('id')
					param_obj = self.enums.create(cat_id)
					param_obj.read_xml(inpart)
			if x_part.tag == 'params':
				for inpart in x_part:
					cat_id = inpart.get('id')
					if inpart.tag == 'customunit':
						param_obj = self.params.get(cat_id)
						param_obj.unit = 'custom'
						param_obj.unit_custom = datapack_param_custom_unit()
						param_obj.unit_custom.read_xml(inpart, param_obj)
					else:
						param_obj = self.params.create(cat_id)
						param_obj.read_xml(inpart)
			if x_part.tag == 'datavals':
				for inpart in x_part:
					if inpart.tag != 'customunit':
						cat_id = inpart.get('id')
						param_obj = self.datavals.create(cat_id)
						param_obj.read_xml(inpart)
			elif x_part.tag == 'data':
				partattrib = x_part.attrib
				for k, v in partattrib.items():
					self.data[k] = v
			elif x_part.tag == 'datadef': self.datadef.read_xml(x_part)
			elif x_part.tag == 'visual': self.visual.read_xml(x_part)
			elif x_part.tag == 'midi': self.midi.read_xml(x_part)
			elif x_part.tag == 'drumset':
				cat_id = x_part.get('id')
				drumset_obj = self.drumset.create(cat_id)
				drumset_obj.read_xml(x_part)
			elif x_part.tag == 'extplug_assoc': self.extplug_assoc.read_xml(x_part)
			elif x_part.tag == 'datapack_ext': self.datapack_ext.read_xml(x_part)

	def write_xml(self, xml_data):
		if self.data:
			tempxml = ET.SubElement(xml_data, 'data')
			for k,v in self.data.items(): tempxml.set(k,str(v))
		if self.midi.used: self.midi.write_xml(xml_data)
		if self.visual.is_used(): self.visual.write_xml(xml_data)
		if self.enums.used: 
			tempxml = ET.SubElement(xml_data, 'enums')
			self.enums.write_xml(tempxml, 'enum')
		if self.params.used: 
			tempxml = ET.SubElement(xml_data, 'params')
			self.params.write_xml(tempxml, 'param')
			for k,v in self.params.iter():
				if v.unit=='custom': 
					uxml = ET.SubElement(tempxml, 'customunit')
					uxml.set('id', k)
					v.unit_custom.write_xml(uxml)
		if self.datavals.used: 
			tempxml = ET.SubElement(xml_data, 'datavals')
			self.datavals.write_xml(tempxml, 'dataval')
		if self.extplug_assoc.used:
			tempxml = ET.SubElement(xml_data, 'extplug_assoc')
			self.extplug_assoc.write_xml(tempxml)
		if self.datadef.is_used(): self.datadef.write_xml(xml_data)
		if self.datapack_ext.is_used(): self.datapack_ext.write_xml(xml_data)
		if self.drumset.used: self.drumset.write_xml(xml_data, 'drumset')

	def var_get(self, v_name):
		return self.data[v_name] if v_name in self.data else None

	def var_set(self, v_name, v_value):
		if v_value != None: self.data[v_name] = v_value

def midid_to_num(i_bank, i_patch, i_isdrum): return i_bank*256 + i_patch + int(i_isdrum)*128
def midid_from_num(value): return (value>>8), (value%128), int(bool(value&0b10000000))

class datapack_group:
	__slots__ = ['visual']
	def __init__(self, i_group):
		self.visual = datapack_visual(None)
		if i_group: self.load_dict(i_group)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			if x_part.tag == 'visual': self.visual.read_xml(x_part)

	def write_xml(self, xml_data):
		self.visual.write_xml(xml_data)

class datapack_category:
	def __init__(self, i_category):
		self.cache_ids_vst2 = {}
		self.cache_ids_vst3 = {}
		self.cache_ids_clap = {}
		self.data = {}
		self.colorset = datapack_objectset(datapack_colorset)
		self.groups = datapack_objectset(datapack_group)
		self.objects = datapack_objectset(datapack_object)
		self.ext_datapack_ids = {}
		if i_category: self.load_dict(i_category)

	def read_xml(self, xml_data):
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'group':
				object_obj = self.groups.create(cat_id)
				object_obj.read_xml(x_part)
			elif x_part.tag == 'object':
				object_obj = self.objects.create(cat_id)
				object_obj.read_xml(x_part)
				#extassoc = object_obj.extplug_assoc
				#if extassoc.vst2_id: self.cache_ids_vst2[extassoc.vst2_id] = cat_id
				#if extassoc.vst3_id: self.cache_ids_vst3[extassoc.vst3_id] = cat_id
				#if extassoc.clap_id: self.cache_ids_clap[extassoc.clap_id] = cat_id
			elif x_part.tag == 'colorset':
				object_obj = self.colorset.create(cat_id)
				object_obj.read_xml(x_part)
			elif x_part.tag == 'external_path':
				self.ext_datapack_ids[x_part.get('id')] = x_part.text
			elif x_part.tag == 'data':
				partattrib = x_part.attrib
				for k, v in partattrib.items():
					self.data[k] = v

	def write_xml(self, xml_data, name):
		tempxml = ET.SubElement(xml_data, "category")
		tempxml.set('id', name)
		for k, v in self.ext_datapack_ids.items():
			pathxml = ET.SubElement(tempxml, 'external_path')
			pathxml.set('id', k)
			pathxml.text = v
		if self.groups.used: self.groups.write_xml(tempxml, 'group')
		if self.colorset.used: self.colorset.write_xml(tempxml, 'colorset')
		if self.objects.used: self.objects.write_xml(tempxml, 'object')

class datapack:
	def __init__(self, in_datapack):
		self.categorys = {}
		self.category_list = []
		if in_datapack != None:
			if os.path.exists(in_datapack): self.load_file(in_datapack)

	def load_file(self, input_file):
		self.categorys = {}
		self.category_list = []
		parser = ET.XMLParser()
		xml_data = ET.parse(input_file, parser).getroot()
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'import': 
				self.merge_file(x_part.text)
			if x_part.tag == 'category':
				if cat_id not in self.categorys: self.categorys[cat_id] = datapack_category(None)
				cat_obj = self.categorys[cat_id]
				cat_obj.read_xml(x_part)

	def merge_file(self, input_file):
		parser = ET.XMLParser()
		xml_data = ET.parse(input_file, parser).getroot()
		for x_part in xml_data:
			cat_id = x_part.get('id')
			if x_part.tag == 'category':
				if cat_id not in self.categorys: self.categorys[cat_id] = datapack_category(None)
				cat_obj = self.categorys[cat_id]
				cat_obj.read_xml(x_part)

	def write_xml(self, filename):
		xml_proj = ET.Element("datapack")

		for n, c in self.categorys.items():
			c.write_xml(xml_proj, n)

		outfile = ET.ElementTree(xml_proj)
		ET.indent(outfile, space="  ", level=0)
		outfile.write(filename)

	def category_add(self, c_name):
		if c_name not in self.categorys: 
			self.categorys[c_name] = datapack_category(None)
			self.category_list.append(c_name)
		return self.categorys[c_name]

	def category_del(self, c_name):
		if c_name in self.categorys: 
			del self.categorys[c_name]
			self.category_list.remove(c_name)
			return True
		else:
			return False
