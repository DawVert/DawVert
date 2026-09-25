import xml.etree.ElementTree as ET
from objects.file_proj._dawproject import param
from objects.file_proj._dawproject import points

class dawproject_audio:
	def __init__(self, xml_data=None):
		self.algorithm = None
		self.channels = None
		self.duration = None
		self.sampleRate = None
		self.id = None
		self.file = param.dawproject_param_path('File')
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'algorithm' in xml_data.attrib: self.algorithm = xml_data.attrib['algorithm']
		if 'channels' in xml_data.attrib: self.channels = int(xml_data.attrib['channels'])
		if 'duration' in xml_data.attrib: self.duration = float(xml_data.attrib['duration'])
		if 'sampleRate' in xml_data.attrib: self.sampleRate = int(xml_data.attrib['sampleRate'])
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'File': self.file.read(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Audio')
		if self.algorithm != None: tempxml.set('algorithm', self.algorithm)
		if self.channels != None: tempxml.set('channels', str(self.channels))
		if self.sampleRate != None: tempxml.set('sampleRate', str(self.sampleRate))
		if self.duration != None: tempxml.set('duration', str(self.duration))
		if self.id != None: tempxml.set('id', self.id)
		self.file.write(tempxml)

class dawproject_warppoint:
	def __init__(self, xml_data=None):
		self.time = None
		self.contentTime = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'contentTime' in xml_data.attrib: self.contentTime = float(xml_data.attrib['contentTime'])

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Warp')
		if self.time != None: tempxml.set('time', str(self.time))
		if self.contentTime != None: tempxml.set('contentTime', str(self.contentTime))

class dawproject_warps:
	def __init__(self, xml_data=None):
		self.contentTimeUnit = None
		self.timeUnit = None
		self.id = None
		self.points = []
		self.audio = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'contentTimeUnit' in xml_data.attrib: self.contentTimeUnit = xml_data.attrib['contentTimeUnit']
		if 'timeUnit' in xml_data.attrib: self.timeUnit = xml_data.attrib['timeUnit']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Warp': 
				self.points.append(dawproject_warppoint(warppoint_obj))
			if x_part.tag == 'Audio': 
				self.audio = dawproject_audio(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Warps')
		if self.contentTimeUnit != None: tempxml.set('contentTimeUnit', self.contentTimeUnit)
		if self.timeUnit != None: tempxml.set('timeUnit', self.timeUnit)
		if self.id != None: tempxml.set('id', self.id)
		if self.audio != None: self.audio.write(tempxml)
		for x in self.points: x.write(tempxml)

class dawproject_note:
	def __init__(self, xml_data=None):
		self.time = None
		self.duration = None
		self.channel = None
		self.key = None
		self.vel = None
		self.rel = None
		self.points = None
		self.lanes = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'duration' in xml_data.attrib: self.duration = float(xml_data.attrib['duration'])
		if 'channel' in xml_data.attrib: self.channel = int(xml_data.attrib['channel'])
		if 'key' in xml_data.attrib: self.key = int(xml_data.attrib['key'])
		if 'vel' in xml_data.attrib: self.vel = float(xml_data.attrib['vel'])
		if 'rel' in xml_data.attrib: self.rel = float(xml_data.attrib['rel'])
		for x_part in xml_data:
			if x_part.tag == 'Points':
				self.points = points.dawproject_points(x_part)
			if x_part.tag == 'Lanes':
				self.lanes = dawproject_lane(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Note')
		if self.time != None: tempxml.set('time', str(self.time))
		if self.duration != None: tempxml.set('duration', str(self.duration))
		if self.channel != None: tempxml.set('channel', str(self.channel))
		if self.key != None: tempxml.set('key', str(self.key))
		if self.vel != None: tempxml.set('vel', str(self.vel))
		if self.rel != None: tempxml.set('rel', str(self.rel))
		if self.points: self.points.write(tempxml, 'Points')
		if self.lanes: self.lanes.write(tempxml)

class dawproject_notes:
	def __init__(self, xml_data=None):
		self.notes = []
		self.id = ''
		self.points = []
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Note': 
				self.notes.append(dawproject_note(x_part))
			if x_part.tag == 'Points': 
				self.points.append(points.dawproject_points(x_part))

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Notes')
		if self.id: tempxml.set('id', self.id)
		for x in self.notes: x.write(tempxml)
		for x in self.points: x.write(tempxml, 'Points')

class dawproject_clip:
	def __init__(self, xml_data=None):
		self.time = None
		self.duration = None
		self.timeUnit = None
		self.playStart = None
		self.playStop = None
		self.loopStart = None
		self.loopEnd = None
		self.fadeTimeUnit = None
		self.fadeInTime = None
		self.fadeOutTime = None
		self.enable = True
		self.name = None
		self.color = None
		self.insideclips = None
		self.clips = None
		self.notes = None
		self.warps = None
		self.audio = None
		self.lanes = None
		self.contentTimeUnit = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'time' in xml_data.attrib: self.time = float(xml_data.attrib['time'])
		if 'duration' in xml_data.attrib: self.duration = float(xml_data.attrib['duration'])
		if 'timeUnit' in xml_data.attrib: self.timeUnit = xml_data.attrib['timeUnit']
		if 'contentTimeUnit' in xml_data.attrib: self.contentTimeUnit = xml_data.attrib['contentTimeUnit']
		if 'playStart' in xml_data.attrib: self.playStart = float(xml_data.attrib['playStart'])
		if 'loopStart' in xml_data.attrib: self.loopStart = float(xml_data.attrib['loopStart'])
		if 'playStop' in xml_data.attrib: self.playStop = float(xml_data.attrib['playStop'])
		if 'loopEnd' in xml_data.attrib: self.loopEnd = float(xml_data.attrib['loopEnd'])
		if 'fadeTimeUnit' in xml_data.attrib: self.fadeTimeUnit = xml_data.attrib['fadeTimeUnit']
		if 'fadeInTime' in xml_data.attrib: self.fadeInTime = float(xml_data.attrib['fadeInTime'])
		if 'fadeOutTime' in xml_data.attrib: self.fadeOutTime = float(xml_data.attrib['fadeOutTime'])
		if 'name' in xml_data.attrib: self.name = xml_data.attrib['name']
		if 'color' in xml_data.attrib: self.color = xml_data.attrib['color']
		if 'enable' in xml_data.attrib: self.enable = xml_data.attrib['enable']=='true'
		for x_part in xml_data:
			if x_part.tag == 'Clips': self.clips = dawproject_clips(x_part)
			if x_part.tag == 'Notes': self.notes = dawproject_notes(x_part)
			if x_part.tag == 'Warps': self.warps = dawproject_warps(x_part)
			if x_part.tag == 'Audio': self.audio = dawproject_audio(x_part)
			if x_part.tag == 'Lanes': self.lanes = dawproject_lane(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Clip')
		if self.time != None: tempxml.set('time', str(self.time))
		if self.duration != None: tempxml.set('duration', str(self.duration))
		if self.timeUnit != None: tempxml.set('timeUnit', str(self.timeUnit))
		if self.contentTimeUnit != None: tempxml.set('contentTimeUnit', self.contentTimeUnit)
		if self.playStart != None: tempxml.set('playStart', str(self.playStart))
		if self.playStop != None: tempxml.set('playStop', str(self.playStop))
		if self.loopStart != None: tempxml.set('loopStart', str(self.loopStart))
		if self.loopEnd != None: tempxml.set('loopEnd', str(self.loopEnd))
		if self.fadeTimeUnit != None: tempxml.set('fadeTimeUnit', str(self.fadeTimeUnit))
		if self.fadeInTime != None: tempxml.set('fadeInTime', str(self.fadeInTime))
		if self.fadeOutTime != None: tempxml.set('fadeOutTime', str(self.fadeOutTime))
		tempxml.set('enable', 'true' if self.enable else 'false')
		if self.name != None: tempxml.set('name', str(self.name))
		if self.color != None: tempxml.set('color', str(self.color))
		if self.clips: self.clips.write(tempxml)
		if self.notes: self.notes.write(tempxml)
		if self.warps: self.warps.write(tempxml)
		if self.audio: self.audio.write(tempxml)
		if self.lanes: self.lanes.write(tempxml)

class dawproject_clips:
	def __init__(self, xml_data=None):
		self.clips = []
		self.id = ''
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		for x_part in xml_data:
			if x_part.tag == 'Clip': 
				self.clips.append(dawproject_clip(x_part))

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Clips')
		if self.id: tempxml.set('id', self.id)
		for x in self.clips: x.write(tempxml)

class dawproject_lane:
	def __init__(self, xml_data=None):
		self.clips = None
		self.warps = None
		self.audio = None
		self.notes = None
		self.points = []
		self.track = ''
		self.id = ''
		self.fadeTimeUnit = None
		self.fadeInTime = None
		self.fadeOutTime = None
		if xml_data is not None: self.read(xml_data)

	def read(self, xml_data):
		if 'track' in xml_data.attrib: self.track = xml_data.attrib['track']
		if 'id' in xml_data.attrib: self.id = xml_data.attrib['id']
		if 'fadeTimeUnit' in xml_data.attrib: self.fadeTimeUnit = xml_data.attrib['fadeTimeUnit']
		if 'fadeInTime' in xml_data.attrib: self.fadeInTime = float(xml_data.attrib['fadeInTime'])
		if 'fadeOutTime' in xml_data.attrib: self.fadeOutTime = float(xml_data.attrib['fadeOutTime'])
		for x_part in xml_data:
			if x_part.tag == 'Clips': self.clips = dawproject_clips(x_part)
			if x_part.tag == 'Warps': self.warps = dawproject_warps(x_part)
			if x_part.tag == 'Points': self.points.append(points.dawproject_points(x_part))
			if x_part.tag == 'Audio': self.audio = dawproject_audio(x_part)
			if x_part.tag == 'Notes': self.notes = dawproject_notes(x_part)

	def write(self, xmltag):
		tempxml = ET.SubElement(xmltag, 'Lanes')
		if self.track: tempxml.set('track', self.track)
		if self.id: tempxml.set('id', self.id)
		if self.clips: self.clips.write(tempxml)
		if self.warps: self.warps.write(tempxml)
		if self.audio: self.audio.write(tempxml)
		if self.notes: self.notes.write(tempxml)
		if self.fadeTimeUnit != None: tempxml.set('fadeTimeUnit', str(self.fadeTimeUnit))
		if self.fadeInTime != None: tempxml.set('fadeInTime', str(self.fadeInTime))
		if self.fadeOutTime != None: tempxml.set('fadeOutTime', str(self.fadeOutTime))
		for x in self.points: x.write(tempxml, 'Points')
