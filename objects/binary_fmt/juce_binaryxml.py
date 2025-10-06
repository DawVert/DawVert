# SPDX-FileCopyrightText: 2025 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from lxml import etree as ET
from external.easybinrw import easybinrw

VERBOSE = False
def read_number(ebrw_readstr):
	intlen = ebrw_readstr.int_u8()
	out = 0
	if intlen == 1: out = ebrw_readstr.int_u8()
	if intlen == 2: out = ebrw_readstr.int_u16()
	if intlen == 3: out = ebrw_readstr.int_u24()
	if intlen == 4: out = ebrw_readstr.int_u32()
	if VERBOSE: print(intlen, out)
	return out

def write_number(ebrw_writestr, val):
	if val>0xFFFFFF: 
		ebrw_writestr.int_u8(4)
		ebrw_writestr.int_u32(val)
	elif val>0xFFFF: 
		ebrw_writestr.int_u8(3)
		ebrw_writestr.int_u16(val&0xFFFF)
		ebrw_writestr.int_u8(val>>16)
	elif val>0xFF: 
		ebrw_writestr.int_u8(2)
		ebrw_writestr.int_u16(val)
	elif val:
		ebrw_writestr.int_u8(1)
		ebrw_writestr.int_u8(val)
	else:
		ebrw_writestr.int_u8(0)

class juce_binaryxml_object:
	__slots__ = ['type', 'data']
	def __init__(self):
		self.type = 0
		self.data = None

	def __repr__(self):
		return '<BinXML Object - Type: %s, Value:"%s">' % (str(self.type), str(self.data))

	def __int__(self): return int(self.data)
	def __float__(self): return float(self.data)
	def __bool__(self): return bool(self.data)
	def __str__(self): 
		if self.type == 1: return str(self.data)
		elif self.type == 2: return 'true'
		elif self.type == 3: return 'false'
		elif self.type == 4: return str(self.data)
		elif self.type == 5: return self.data
		elif self.type == 6: return str(self.data)
		elif self.type == 8: return str(self.data)
		return str(self.data)

	def read_ebrw(self, ebrw_readstr):
		ebrw_readstr.isolate_size(read_number(ebrw_readstr))
		self.type = ebrw_readstr.int_u8()
		if self.type == 1: self.data = ebrw_readstr.int_u32()
		elif self.type == 2: self.data = True
		elif self.type == 3: self.data = False
		elif self.type == 4: self.data = ebrw_readstr.double()
		elif self.type == 5: self.data = ebrw_readstr.string_t()
		elif self.type == 6: self.data = ebrw_readstr.int_u64()
		elif self.type == 8: self.data = ebrw_readstr.rest()
		else: raise ValueError('binaryxml: unknown datatype %i' % self.type)
		ebrw_readstr.isolate_end()

	def to_bytes(self, ebrw_writestr):
		ebrw_writestr = easybinrw.binwrite()
		self.write_ebrw(ebrw_writestr)
		return ebrw_writestr.getvalue()

	def write_ebrw(self, ebrw_writestr):
		if self.type:
			out__ebrw_writestr = easybinrw.binwrite()
			out__ebrw_writestr.int_u8(self.type)
			if self.type == 1: out__ebrw_writestr.int_u32(min(self.data, 2147483647))
			elif self.type == 4: out__ebrw_writestr.double(self.data)
			elif self.type == 5: out__ebrw_writestr.string_t(self.data)
			elif self.type == 6: out__ebrw_writestr.int_u64(self.data)
			elif self.type == 8: out__ebrw_writestr.raw(self.data)
			outdata = out__ebrw_writestr.getvalue()
			write_number(ebrw_writestr, len(outdata))
			ebrw_writestr.raw(outdata)

	def set(self, value):
		if isinstance(value, str):
			self.type = 5
			self.data = value
		if isinstance(value, bool):
			self.type = 2 if value else 3
			self.data = value
		if isinstance(value, int):
			self.type = 1
			self.data = value
		if isinstance(value, float):
			self.type = 4
			self.data = value
			
	def to_xml_attrib(self, name, xmldata):
		if self.type: xmldata.set(name, str(self))
			
class juce_binaryxml_element:
	__slots__ = ['tag', 'attrib', 'children']
	def __init__(self):
		self.tag = ''
		self.attrib = {}
		self.children = []

	def get_attrib_native(self):
		return dict([(k, v.data) for (k, v) in self.attrib.items()])

	def add_child(self, tag):
		jg_child = juce_binaryxml_element()
		jg_child.tag = tag
		self.children.append(jg_child)
		return jg_child

	def get(self, name):
		return self.attrib[name] if name in self.attrib else None

	def set(self, name, value):
		jobj = juce_binaryxml_object()
		jobj.set(value)
		self.attrib[name] = jobj

	def __repr__(self):
		return '<BinXML Group - "%s">' % (str(self.tag))

	def __bool__(self):
		return bool(self.children)

	def __iter__(self):
		for x in self.children: yield x

	def __len__(self):
		return len(self.children)

	def read_bytes(self, inbytes):
		ebrw_readstr = easybinrw.binread()
		ebrw_readstr.load_data(inbytes)
		try: self.read_ebrw(ebrw_readstr)
		except: pass

	def read_ebrw(self, ebrw_readstr):
		self.tag = ebrw_readstr.string_t()
		for _ in range(read_number(ebrw_readstr)):
			aname = ebrw_readstr.string_t()
			b_obj = juce_binaryxml_object()
			b_obj.read_ebrw(ebrw_readstr)
			if aname == 'data': print(aname, b_obj.type)
			self.attrib[aname] = b_obj

		for _ in range(read_number(ebrw_readstr)):
			subele = juce_binaryxml_element()
			subele.read_ebrw(ebrw_readstr)
			self.children.append(subele)

	def write_ebrw(self, ebrw_writestr):
		ebrw_writestr.string_t(self.tag)
		write_number(ebrw_writestr, len(self.attrib))
		for k, v in self.attrib.items():
			ebrw_writestr.string_t(k)
			v.write_ebrw(ebrw_writestr)

		write_number(ebrw_writestr, len(self.children))
		for x in self.children:
			x.write_ebrw(ebrw_writestr)

	def to_bytes(self):
		ebrw_writestr = easybinrw.binwrite()
		self.write_ebrw(ebrw_writestr)
		return ebrw_writestr.getvalue()

	def to_xml(self, xmldata):
		xml_part = ET.SubElement(xmldata, self.tag)
		for k, v in self.attrib.items(): v.to_xml_attrib(k, xml_part)
		for x in self.children: x.to_xml(xml_part)

	def to_xml_root(self):
		xml_part = ET.Element(self.tag)
		for k, v in self.attrib.items(): v.to_xml_attrib(k, xml_part)
		for x in self.children: x.to_xml(xml_part)
		return xml_part

	def output_file(self, filename):
		outfile = ET.ElementTree(self.to_xml_root())
		ET.indent(outfile)
		outfile.write(filename, encoding='utf-8', xml_declaration = True)