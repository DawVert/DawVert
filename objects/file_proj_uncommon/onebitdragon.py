# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_values
from io import BytesIO
from objects.exceptions import ProjectFileParserException
import base64
import json
import zlib

# ============================================= instrument ============================================= 

class onebitd_instrument:
	def __init__(self, indict=None):
		self.on = True
		self.volume = 1
		self.audioClipId = 'none'
		self.preset = None
		self.accompanimentId = None
		self.accompaniment = None
		self.presetAccompaniment = None
		self.arpeggiatorId = None
		self.arpeggiator = None
		self.presetArpeggiator = None
		self.offset = None
		self.noteDuration = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'on' in indict: self.on = indict['on']
		if 'volume' in indict: self.volume = indict['volume']
		if 'audioClipId' in indict: self.audioClipId = indict['audioClipId']
		if 'preset' in indict: self.preset = indict['preset']
		if 'accompanimentId' in indict: self.accompanimentId = indict['accompanimentId']
		if 'accompaniment' in indict: self.accompaniment = indict['accompaniment']
		if 'presetAccompaniment' in indict: self.presetAccompaniment = indict['presetAccompaniment']
		if 'arpeggiatorId' in indict: self.arpeggiatorId = indict['arpeggiatorId']
		if 'arpeggiator' in indict: self.arpeggiator = indict['arpeggiator']
		if 'presetArpeggiator' in indict: self.presetArpeggiator = indict['presetArpeggiator']
		if 'offset' in indict: self.offset = indict['offset']
		if 'noteDuration' in indict: self.noteDuration = indict['noteDuration']

	def get_instid(self):
		return 'inst'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

class onebitd_drum:
	def __init__(self, indict=None):
		self.on = True
		self.euclidean = None
		self.audioClipId = 'none'
		self.beats = None
		self.loop = None
		self.offset = None
		self.volume = 1
		self.preset = None
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'on' in indict: self.on = indict['on']
		if 'euclidean' in indict: self.euclidean = indict['euclidean']
		if 'audioClipId' in indict: self.audioClipId = indict['audioClipId']
		if 'beats' in indict: self.beats = indict['beats']
		if 'loop' in indict: self.loop = indict['loop']
		if 'offset' in indict: self.offset = indict['offset']
		if 'volume' in indict: self.volume = indict['volume']
		if 'preset' in indict: self.preset = indict['preset']

	def get_instid(self):
		return 'drum'+'_'.join([str(int(self.on)), str(self.audioClipId), str(self.volume)])

# ============================================= song ============================================= 

class onebitd_block:
	def __init__(self, indict=None):
		self.isEmpty = True
		self.repeat = False
		self.state = 99
		self.columns = []
		self.drums = []
		self.instruments = []
		self.n_drums = [[] for x in range(5)]
		self.n_inst = [[[] for x in range(16)] for x in range(4)]
		if indict is not None: self.read(indict)

	def read(self, indict):
		if 'isEmpty' in indict: self.isEmpty = indict['isEmpty']
		if 'repeat' in indict: self.repeat = indict['repeat']
		if 'state' in indict: self.state = indict['state']
		if 'columns' in indict: self.columns = indict['columns']
		if 'drums' in indict: self.drums = [onebitd_drum(x) for x in indict['drums']]
		if 'instruments' in indict: self.instruments = [onebitd_instrument(x) for x in indict['instruments']]

		if 'notes' in indict:
			notesdata = indict['notes']
			datafirst = data_values.list__chunks(notesdata, 9*128)
			for firstnum in range(len(datafirst)):
				datasecond = datafirst[firstnum]
				datathird = data_values.list__chunks(datasecond, 9)
				for thirdnum in range(128):
					stepnum = ((thirdnum&0b0000111)<<4)+((thirdnum&0b1111000)>>3)
					forthdata = datathird[thirdnum]
					for notevirt in range(9):
						notevirt_t = -notevirt+8 + firstnum*9
						if 'velocity' in forthdata[notevirt]:
							if forthdata[notevirt]['velocity'] != 0.0:
								tnotedata = [stepnum, forthdata[notevirt]]
								if notevirt_t < 5: self.n_drums[notevirt_t].append(tnotedata)
								else:
									instnumber = notevirt_t-5
									notenumber = instnumber//9
									instnumber -= (instnumber//9)*9
									self.n_inst[instnumber][notenumber].append(tnotedata)

class onebitd_song:
	def __init__(self):
		self.version = None
		self.reverb = False
		self.bpm = 120
		self.scaleId = 0
		self.volume = 1
		self.blocks = []

	def load_from_file(self, input_file):

		try:
			song_file = open(input_file, 'r')
			filetxt = song_file.read()
		except UnicodeDecodeError:
			raise ProjectFileParserException('1bitdragon: File is not text')

		basebase64stream = base64.b64decode(filetxt)
		bio_base64stream = BytesIO(basebase64stream)
		bio_base64stream.seek(4)
		
		try: 
			decompdata = json.loads(zlib.decompress(bio_base64stream.read(), 16+zlib.MAX_WBITS))
		except zlib.error as t:
			raise ProjectFileParserException('1bitdragon: '+str(t))

		self.version = decompdata['version'] if 'version' in decompdata else None
		self.reverb = decompdata['reverb']
		self.bpm = decompdata['bpm']
		self.scaleId = decompdata['scaleId']
		self.volume = decompdata['volume']
		self.blocks = [onebitd_block(x) for x in decompdata['blocks']]
		return True