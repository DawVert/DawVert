# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import shlex
from functions import data_values
from functions import xtramath

from objects.inst_params import fm_vrc7
from objects.inst_params import fm_epsm
from objects.exceptions import ProjectFileParserException

import logging
logger_projparse = logging.getLogger('projparse')

DEBUG_IN_OUT = False

def get_bpm(Groove, BeatLength):
	return 60/(xtramath.average(Groove)/60*BeatLength)

def read_regs(cmd_params, startname, size):
	regdata = [0 for x in range(size)]
	for regnum in range(size):
		regname = startname+str(regnum)
		if regname in cmd_params: regdata[regnum] = int(cmd_params[regname])
	return regdata

class dpcm_sample:
	def __init__(self):
		self.Name = ''
		self.Color = None
		self.Data = b''
		#if data: self.data_bytes = bytes.fromhex(self.data_txt)

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Color' in cmd_params: self.Color = cmd_params['Color']
		if 'Data' in cmd_params: self.Data = cmd_params['Data']

	def write(self, block_obj):
		block_obj.name = 'DPCMSample'
		cmd_params = block_obj.attrib
		if self.Name: cmd_params['Name'] = self.Name
		if self.Color: cmd_params['Color'] = self.Color
		if self.Data: cmd_params['Data'] = self.Data

class dpcm_mapping:
	def __init__(self):
		self.Note = ''
		self.Sample = ''
		self.Pitch = 15
		self.Loop = False
		self.Bank = -1

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Note' in cmd_params: self.Note = cmd_params['Note']
		if 'Sample' in cmd_params: self.Sample = cmd_params['Sample']
		if 'Pitch' in cmd_params: self.Pitch = int(cmd_params['Pitch'])
		if 'Loop' in cmd_params: self.Loop = cmd_params['Loop']
		if 'Bank' in cmd_params: self.Bank = int(cmd_params['Bank'])

	def write(self, block_obj):
		block_obj.name = 'DPCMMapping'
		cmd_params = block_obj.attrib
		cmd_params['Note'] = self.Note
		cmd_params['Sample'] = self.Sample
		cmd_params['Pitch'] = self.Pitch
		cmd_params['Loop'] = self.Loop
		if self.Bank>-1: cmd_params['Bank'] = self.Bank

class fs_arpeggio:
	def __init__(self):
		self.Values = []
		self.Length = 0
		self.Loop = 0
		self.Name = ''
		self.Color = ''

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Values' in cmd_params: self.Values = [int(x) for x in cmd_params['Values'].split(',')]
		if 'Length' in cmd_params: self.Length = int(cmd_params['Length'])
		if 'Loop' in cmd_params: self.Loop = int(cmd_params['Loop'])
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Color' in cmd_params: self.Color = cmd_params['Color']

	def write(self, block_obj):
		block_obj.name = 'Arpeggio'
		cmd_params = block_obj.attrib
		cmd_params['Name'] = self.Name
		if self.Color: cmd_params['Color'] = self.Color
		cmd_params['Length'] = self.Length
		cmd_params['Loop'] = self.Loop
		cmd_params['Values'] = ','.join([str(x) for x in self.Values])

class fs_envelope:
	def __init__(self):
		self.Type = ''
		self.Values = []
		self.Length = 0
		self.Loop = -1
		self.Relative = False
		self.Release = -1

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Values' in cmd_params: 
			self.Values = [int(x) for x in cmd_params['Values'].split(',')]
			self.Length = len(self.Values)
		if 'Length' in cmd_params: self.Length = int(cmd_params['Length'])
		if 'Loop' in cmd_params: self.Loop = int(cmd_params['Loop']) 
		if 'Release' in cmd_params: self.Release = int(cmd_params['Release'])
		if 'Type' in cmd_params: self.Type = cmd_params['Type']
		if 'Relative' in cmd_params: self.Relative = cmd_params['Relative']=='True'

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Type'] = self.Type
		if self.Length: cmd_params['Length'] = self.Length
		if self.Loop>-1: cmd_params['Loop'] = self.Loop
		if self.Release>-1: cmd_params['Release'] = self.Release
		if self.Relative: cmd_params['Relative'] = 'True'
		if self.Values: cmd_params['Values'] = ','.join([str(x) for x in self.Values])

class fs_instrument:
	def __init__(self):
		self.Name = ''
		self.Color = ''
		self.Expansion = ''
		self.DPCMMappings = []
		self.Arpeggio = {}
		self.Envelopes = []

		self.FdsWavePreset = 'Custom'
		self.FdsModPreset = 'Custom'
		self.FdsMasterVolume = 0

		self.Vrc7Patch = 0
		self.Vrc7Regs = []

		self.Vrc6SawMasterVolume = ''

		self.N163WavePreset = ''
		self.N163WaveSize = 0
		self.N163WavePos = 0
		self.N163WaveCount = 0

		self.S5BEnvelopeShape = 0
		self.S5BEnvelopeAutoPitch = True
		self.S5BEnvelopeAutoPitchOctave = 3
		self.S5BEnvelopePitch = 1000

		self.EpsmPatch = 0
		self.EpsmRegs = []

		self.EPSMSquareEnvelopeShape = 0
		self.EPSMSquareEnvelopeAutoPitch = True
		self.EPSMSquareEnvelopeAutoPitchOctave = 3

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Color' in cmd_params: self.Color = cmd_params['Color']
		if 'Expansion' in cmd_params: self.Expansion = cmd_params['Expansion']
		if 'N163WavePreset' in cmd_params: self.N163WavePreset = cmd_params['N163WavePreset']
		if 'N163WaveSize' in cmd_params: self.N163WaveSize = int(cmd_params['N163WaveSize'])
		if 'N163WavePos' in cmd_params: self.N163WavePos = int(cmd_params['N163WavePos'])
		if 'N163WaveCount' in cmd_params: self.N163WaveCount = int(cmd_params['N163WaveCount'])
		if 'Vrc6SawMasterVolume' in cmd_params: self.Vrc6SawMasterVolume = cmd_params['Vrc6SawMasterVolume']
		if 'EpsmPatch' in cmd_params: self.EpsmPatch = int(cmd_params['EpsmPatch'])
		if 'EPSMSquareEnvelopeShape' in cmd_params: self.EPSMSquareEnvelopeShape = int(cmd_params['EPSMSquareEnvelopeShape'])
		if 'EPSMSquareEnvelopeAutoPitch' in cmd_params: self.EPSMSquareEnvelopeAutoPitch = cmd_params['EPSMSquareEnvelopeAutoPitch']=='True'
		if 'EPSMSquareEnvelopeAutoPitchOctave' in cmd_params: self.EPSMSquareEnvelopeAutoPitchOctave = int(cmd_params['EPSMSquareEnvelopeAutoPitchOctave'])
		if 'Vrc7Patch' in cmd_params: self.Vrc7Patch = int(cmd_params['Vrc7Patch'])
		if 'FdsWavePreset' in cmd_params: self.FdsWavePreset = cmd_params['FdsWavePreset']
		if 'FdsModPreset' in cmd_params: self.FdsModPreset = cmd_params['FdsModPreset']
		if 'FdsMasterVolume' in cmd_params: self.FdsMasterVolume = int(cmd_params['FdsMasterVolume'])
		if 'S5BEnvelopeShape' in cmd_params: self.S5BEnvelopeShape = int(cmd_params['S5BEnvelopeShape'])
		if 'S5BEnvelopeAutoPitch' in cmd_params: self.S5BEnvelopeAutoPitch = cmd_params['S5BEnvelopeAutoPitch']=='True'
		if 'S5BEnvelopeAutoPitchOctave' in cmd_params: self.S5BEnvelopeAutoPitchOctave = int(cmd_params['S5BEnvelopeAutoPitchOctave'])
		if 'S5BEnvelopePitch' in cmd_params: self.S5BEnvelopePitch = int(cmd_params['S5BEnvelopePitch'])
		self.Vrc7Regs = read_regs(cmd_params, 'Vrc7Reg', 8)
		self.EpsmRegs = read_regs(cmd_params, 'EpsmReg', 31)

		for i in block_obj:
			if i.name == 'Envelope': 
				o = fs_envelope()
				o.read(i)
				self.Envelopes.append(o)

			if i.name == 'DPCMMapping': 
				o = dpcm_mapping()
				o.read(i)
				self.DPCMMappings.append(o)

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		if self.Name: cmd_params['Name'] = self.Name
		if self.Color: cmd_params['Color'] = self.Color
		if self.Expansion: cmd_params['Expansion'] = self.Expansion
		if self.Expansion=='FDS':
			cmd_params['FdsWavePreset'] = self.FdsWavePreset
			cmd_params['FdsModPreset'] = self.FdsModPreset
			if self.FdsMasterVolume: cmd_params['FdsMasterVolume'] = self.FdsMasterVolume
		if self.Expansion=='VRC6':
			cmd_params['Vrc6SawMasterVolume'] = self.Vrc6SawMasterVolume
		if self.Expansion=='S5B':
			cmd_params['S5BEnvelopeShape'] = self.S5BEnvelopeShape
			cmd_params['S5BEnvelopeAutoPitch'] = self.S5BEnvelopeAutoPitch
			cmd_params['S5BEnvelopeAutoPitchOctave'] = self.S5BEnvelopeAutoPitchOctave
			cmd_params['S5BEnvelopePitch'] = self.S5BEnvelopePitch
		if self.Expansion=='N163':
			cmd_params['N163WavePreset'] = self.N163WavePreset
			cmd_params['N163WaveSize'] = self.N163WaveSize
			cmd_params['N163WavePos'] = self.N163WavePos
			cmd_params['N163WaveCount'] = self.N163WaveCount
		if self.Expansion=='EPSM':
			cmd_params['EpsmPatch'] = self.EpsmPatch
			if self.EpsmPatch==0:
				for n, x in enumerate(self.EpsmRegs):
					cmd_params['EpsmReg'+str(n)] = x
			cmd_params['EPSMSquareEnvelopeShape'] = self.EPSMSquareEnvelopeShape
			cmd_params['EPSMSquareEnvelopeAutoPitch'] = self.EPSMSquareEnvelopeAutoPitch
			cmd_params['EPSMSquareEnvelopeAutoPitchOctave'] = self.EPSMSquareEnvelopeAutoPitchOctave
		if self.Expansion=='VRC7':
			cmd_params['Vrc7Patch'] = self.Vrc7Patch
			if self.Vrc7Patch==0:
				for n, x in enumerate(self.Vrc7Regs):
					cmd_params['Vrc7Reg'+str(n)] = x

		for x in self.Envelopes: x.write(block_obj.add_block('Envelope'))
		for x in self.DPCMMappings: x.write(block_obj.add_block('DPCMMapping'))

class fs_note:
	def __init__(self):
		self.Time = 0
		self.Value = ''
		self.Duration = 0
		self.Instrument = ''
		self.SlideTarget = None
		self.Attack = None
		self.FinePitch = None
		self.Volume = None
		self.VolumeSlideTarget = None
		self.VibratoSpeed = None
		self.VibratoDepth = None
		self.Arpeggio = None
		self.Release = None
		self.DutyCycle = None

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Time' in cmd_params: self.Time = int(cmd_params['Time'])
		if 'Value' in cmd_params: self.Value = cmd_params['Value']
		if 'Duration' in cmd_params: self.Duration = cmd_params['Duration']
		if 'Release' in cmd_params: self.Release = int(cmd_params['Release'])
		if 'Instrument' in cmd_params: self.Instrument = cmd_params['Instrument']
		if 'SlideTarget' in cmd_params: self.SlideTarget = cmd_params['SlideTarget']
		if 'Attack' in cmd_params: self.Attack = cmd_params['Attack']
		if 'FinePitch' in cmd_params: self.FinePitch = int(cmd_params['FinePitch'])
		if 'Volume' in cmd_params: self.Volume = int(cmd_params['Volume'])
		if 'VolumeSlideTarget' in cmd_params: self.VolumeSlideTarget = cmd_params['VolumeSlideTarget']
		if 'VibratoSpeed' in cmd_params: self.VibratoSpeed = int(cmd_params['VibratoSpeed'])
		if 'VibratoDepth' in cmd_params: self.VibratoDepth = int(cmd_params['VibratoDepth'])
		if 'Arpeggio' in cmd_params: self.Arpeggio = cmd_params['Arpeggio']
		if 'DutyCycle' in cmd_params: self.DutyCycle = int(cmd_params['DutyCycle'])

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Time'] = self.Time
		if self.Value: cmd_params['Value'] = self.Value
		if self.Duration: cmd_params['Duration'] = self.Duration
		if self.Release: cmd_params['Release'] = self.Release
		if self.Instrument: cmd_params['Instrument'] = self.Instrument
		if self.SlideTarget is not None: cmd_params['SlideTarget'] = self.SlideTarget
		if self.Attack is not None: cmd_params['Attack'] = self.Attack
		if self.Volume is not None: cmd_params['Volume'] = self.Volume
		if self.FinePitch is not None: cmd_params['FinePitch'] = self.FinePitch
		if self.VolumeSlideTarget is not None: cmd_params['VolumeSlideTarget'] = self.VolumeSlideTarget
		if self.VibratoSpeed is not None: cmd_params['VibratoSpeed'] = self.VibratoSpeed
		if self.VibratoDepth is not None: cmd_params['VibratoDepth'] = self.VibratoDepth
		if self.Arpeggio is not None: cmd_params['Arpeggio'] = self.Arpeggio
		if self.DutyCycle is not None: cmd_params['DutyCycle'] = self.DutyCycle

class fs_pattern:
	def __init__(self):
		self.Name = ''
		self.Color = ''
		self.Notes = []

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Color' in cmd_params: self.Color = cmd_params['Color']
		for i in block_obj:
			if i.name == 'Note': 
				o = fs_note()
				o.read(i)
				self.Notes.append(o)

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Name'] = self.Name
		if self.Color: cmd_params['Color'] = self.Color
		for x in self.Notes: x.write(block_obj.add_block('Note'))

class fs_patterncustomsettings:
	def __init__(self):
		self.Time = 4
		self.Length = 16
		self.BeatLength = 4
		self.NoteLength = 4
		self.Groove = []
		self.GroovePaddingMode = 'Middle'

	def get_bpm(self):
		return get_bpm(self.Groove, self.BeatLength)

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Time' in cmd_params: self.Time = int(cmd_params['Time'])
		if 'Length' in cmd_params: self.Length = int(cmd_params['Length'])
		if 'BeatLength' in cmd_params: self.BeatLength = int(cmd_params['BeatLength'])
		if 'NoteLength' in cmd_params: self.NoteLength = int(cmd_params['NoteLength'])
		if 'Groove' in cmd_params: self.Groove = [int(x) for x in cmd_params['Groove'].split('-')]
		if 'GroovePaddingMode' in cmd_params: self.GroovePaddingMode = cmd_params['GroovePaddingMode']

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Time'] = self.Time
		cmd_params['Length'] = self.Length
		cmd_params['NoteLength'] = self.NoteLength
		cmd_params['Groove'] = '-'.join([str(x) for x in self.Groove])
		cmd_params['GroovePaddingMode'] = self.GroovePaddingMode
		cmd_params['BeatLength'] = self.BeatLength

class fs_patterninstance:
	def __init__(self):
		self.Time = 0
		self.Pattern = ''

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Time' in cmd_params: self.Time = int(cmd_params['Time'])
		if 'Pattern' in cmd_params: self.Pattern = cmd_params['Pattern']

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Time'] = self.Time
		cmd_params['Pattern'] = self.Pattern

class fs_channel:
	def __init__(self):
		self.Type = ''
		self.Patterns = []
		self.PatternInstances = []

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Type' in cmd_params: self.Type = cmd_params['Type']
		for i in block_obj:
			if i.name == 'Pattern': 
				o = fs_pattern()
				o.read(i)
				self.Patterns.append(o)
			if i.name == 'PatternInstance': 
				o = fs_patterninstance()
				o.read(i)
				self.PatternInstances.append(o)

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Type'] = self.Type
		for x in self.Patterns: x.write(block_obj.add_block('Pattern'))
		for x in self.PatternInstances: x.write(block_obj.add_block('PatternInstance'))

class fs_song:
	def __init__(self):
		self.Name = ''
		self.Color = None
		self.Length = 1
		self.LoopPoint = 0
		self.PatternLength = 16
		self.BeatLength = 4
		self.NoteLength = 4
		self.Groove = []
		self.GroovePaddingMode = ''
		self.Channels = []
		self.PatternCustomSettings = []

	def get_bpm(self):
		return get_bpm(self.Groove, self.BeatLength)

	def read(self, block_obj):
		cmd_params = block_obj.attrib
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Color' in cmd_params: self.Color = cmd_params['Color']
		if 'Length' in cmd_params: self.Length = int(cmd_params['Length'])
		if 'LoopPoint' in cmd_params: self.LoopPoint = int(cmd_params['LoopPoint'])
		if 'PatternLength' in cmd_params: self.PatternLength = int(cmd_params['PatternLength'])
		if 'BeatLength' in cmd_params: self.BeatLength = int(cmd_params['BeatLength'])
		if 'NoteLength' in cmd_params: self.NoteLength = int(cmd_params['NoteLength'])
		if 'Groove' in cmd_params: self.Groove = [int(x) for x in cmd_params['Groove'].split('-')]
		if 'GroovePaddingMode' in cmd_params: self.GroovePaddingMode = cmd_params['GroovePaddingMode']

		for i in block_obj:
			if i.name == 'Channel': 
				o = fs_channel()
				o.read(i)
				self.Channels.append(o)

			if i.name == 'PatternCustomSettings': 
				o = fs_patterncustomsettings()
				o.read(i)
				self.PatternCustomSettings.append(o)

	def write(self, block_obj):
		cmd_params = block_obj.attrib
		cmd_params['Name'] = self.Name
		if self.Color: cmd_params['Color'] = self.Color
		cmd_params['Length'] = self.Length
		cmd_params['LoopPoint'] = self.LoopPoint
		cmd_params['PatternLength'] = self.PatternLength
		cmd_params['BeatLength'] = self.BeatLength
		cmd_params['NoteLength'] = self.NoteLength
		cmd_params['Groove'] = '-'.join([str(x) for x in self.Groove])
		cmd_params['GroovePaddingMode'] = self.GroovePaddingMode

		for x in self.PatternCustomSettings: x.write(block_obj.add_block('PatternCustomSettings'))
		for x in self.Channels: x.write(block_obj.add_block('Channel'))

def parse_line(line):
	t_cmd = line.split(" ", 1)
	t_precmd = t_cmd[0]
	tabs_num = t_precmd.count('\t')
	cmd_name = t_precmd.split()[0]
	cmd_params = dict(token.split('=') for token in shlex.split(t_cmd[1]))
	return cmd_name, cmd_params

class famistudiotxt_block:
	def __init__(self):
		self.name = ''
		self.attrib = {}
		self.children = []

		self.decoded = False
		self.temp_root = []
		self.temp_children = []

	def __iter__(self):
		return self.children.__iter__()

	def __repr__(self):
		return '<FamiStudio Block - %s>' % self.name

	def add_block(self, name):
		child = famistudiotxt_block()
		child.name = name
		self.children.append(child)
		return child

	def lines_read(self, lines):
		root_found = False
		while lines:
			numtabs, data = lines[0]
			numtabs = numtabs
			if not numtabs:
				if not root_found:
					root_found = True
					self.temp_root = data
				else: break
			else:
				self.temp_children.append([numtabs-1, data])
			lines.pop(0)

	def lines_parse(self):
		self.name, self.attrib = self.temp_root
		while self.temp_children:
			child = famistudiotxt_block()
			child.lines_read(self.temp_children)
			child.name, child.attrib = child.temp_root
			child.lines_parse()
			self.children.append(child)

	def load_from_file(self, input_file):
		try:
			fs_file = open(input_file, 'r')
			famistudiotxt_lines = fs_file.readlines()
		except UnicodeDecodeError:
			raise ProjectFileParserException('famistudio_txt: File is not text')

		lines = []
		for x in famistudiotxt_lines:
			o = x.rsplit('\t', 1)
			if len(o)==2:
				numtabs, data = o
				numtabs = len(numtabs)+1
			else:
				numtabs = 0
				data = o[0]
			lines.append([numtabs, parse_line(data.strip())])
		self.lines_read(lines)
		self.lines_parse()

	def write(self, f, numtabs):
		o = (numtabs*'\t')+self.name
		for k, v in self.attrib.items(): o += ' %s="%s"'% (k, str(v))
		o += '\n'
		f.write(o)
		for x in self.children:
			x.write(f, numtabs+1)

	def save_to_file(self, output_file):
		f = open(output_file, 'w')
		self.write(f, 0)


class famistudiotxt_project:
	def __init__(self):
		self.Version = ''
		self.TempoMode = ''
		self.Name = ''
		self.Author = ''
		self.Copyright = ''
		self.Expansions = []
		self.NumN163Channels = 0

		self.Songs = []
		self.Arpeggios = []
		self.DPCMSamples = []
		self.Instruments = []
		self.DPCMMappings = []

		self.VolumeDb = 0.0
		self.VRC6VolumeDb = 0.0
		self.VRC7VolumeDb = 0.0
		self.FDSVolumeDb = 0.0
		self.MMC5VolumeDb = 0.0
		self.N163VolumeDb = 0.0
		self.S5BVolumeDb = 0.0
		self.EPSMVolumeDb = 0.0

		self.EPSMTrebleDb = 0
		self.EPSMTrebleRolloffHz = -1
		self.FDSTrebleDb = 0
		self.FDSTrebleRolloffHz = -1
		self.MMC5TrebleDb = 0
		self.MMC5TrebleRolloffHz = -1
		self.N163TrebleDb = 0
		self.N163TrebleRolloffHz = -1
		self.S5BTrebleDb = 0
		self.S5BTrebleRolloffHz = -1
		self.TrebleDb = 0
		self.TrebleRolloffHz = -1
		self.VRC6TrebleDb = 0
		self.VRC6TrebleRolloffHz = -1
		self.VRC7TrebleDb = 0
		self.VRC7TrebleRolloffHz = -1

	def read(self, block_obj):
		cmd_params = block_obj.attrib

		if 'Version' in cmd_params: self.Version = cmd_params['Version']
		if 'TempoMode' in cmd_params: self.TempoMode = cmd_params['TempoMode']
		if 'Name' in cmd_params: self.Name = cmd_params['Name']
		if 'Author' in cmd_params: self.Author = cmd_params['Author']
		if 'Copyright' in cmd_params: self.Copyright = cmd_params['Copyright']
		if 'Expansions' in cmd_params: self.Expansions = cmd_params['Expansions'].split(',')
		if 'NumN163Channels' in cmd_params: self.NumN163Channels = int(cmd_params['NumN163Channels'])
		if 'VolumeDb' in cmd_params: self.VolumeDb = float(cmd_params['VolumeDb'])
		if 'VRC6VolumeDb' in cmd_params: self.VRC6VolumeDb = float(cmd_params['VRC6VolumeDb'])
		if 'VRC7VolumeDb' in cmd_params: self.VRC7VolumeDb = float(cmd_params['VRC7VolumeDb'])
		if 'FDSVolumeDb' in cmd_params: self.FDSVolumeDb = float(cmd_params['FDSVolumeDb'])
		if 'MMC5VolumeDb' in cmd_params: self.MMC5VolumeDb = float(cmd_params['MMC5VolumeDb'])
		if 'N163VolumeDb' in cmd_params: self.N163VolumeDb = float(cmd_params['N163VolumeDb'])
		if 'S5BVolumeDb' in cmd_params: self.S5BVolumeDb = float(cmd_params['S5BVolumeDb'])
		if 'EPSMVolumeDb' in cmd_params: self.EPSMVolumeDb = float(cmd_params['EPSMVolumeDb'])

		if 'EPSMTrebleDb' in cmd_params: self.EPSMTrebleDb = float(cmd_params['EPSMTrebleDb'])
		if 'EPSMTrebleRolloffHz' in cmd_params: self.EPSMTrebleRolloffHz = float(cmd_params['EPSMTrebleRolloffHz'])
		if 'FDSTrebleDb' in cmd_params: self.FDSTrebleDb = float(cmd_params['FDSTrebleDb'])
		if 'FDSTrebleRolloffHz' in cmd_params: self.FDSTrebleRolloffHz = float(cmd_params['FDSTrebleRolloffHz'])
		if 'MMC5TrebleDb' in cmd_params: self.MMC5TrebleDb = float(cmd_params['MMC5TrebleDb'])
		if 'MMC5TrebleRolloffHz' in cmd_params: self.MMC5TrebleRolloffHz = float(cmd_params['MMC5TrebleRolloffHz'])
		if 'N163TrebleDb' in cmd_params: self.N163TrebleDb = float(cmd_params['N163TrebleDb'])
		if 'N163TrebleRolloffHz' in cmd_params: self.N163TrebleRolloffHz = float(cmd_params['N163TrebleRolloffHz'])
		if 'S5BTrebleDb' in cmd_params: self.S5BTrebleDb = float(cmd_params['S5BTrebleDb'])
		if 'S5BTrebleRolloffHz' in cmd_params: self.S5BTrebleRolloffHz = float(cmd_params['S5BTrebleRolloffHz'])
		if 'TrebleDb' in cmd_params: self.TrebleDb = float(cmd_params['TrebleDb'])
		if 'TrebleRolloffHz' in cmd_params: self.TrebleRolloffHz = float(cmd_params['TrebleRolloffHz'])
		if 'VRC6TrebleDb' in cmd_params: self.VRC6TrebleDb = float(cmd_params['VRC6TrebleDb'])
		if 'VRC6TrebleRolloffHz' in cmd_params: self.VRC6TrebleRolloffHz = float(cmd_params['VRC6TrebleRolloffHz'])
		if 'VRC7TrebleDb' in cmd_params: self.VRC7TrebleDb = float(cmd_params['VRC7TrebleDb'])
		if 'VRC7TrebleRolloffHz' in cmd_params: self.VRC7TrebleRolloffHz = float(cmd_params['VRC7TrebleRolloffHz'])

		for i in block_obj:
			if i.name == 'DPCMSample': 
				o = dpcm_sample()
				o.read(i)
				self.DPCMSamples.append(o)

			if i.name == 'Instrument': 
				o = fs_instrument()
				o.read(i)
				self.Instruments.append(o)

			if i.name == 'Arpeggio': 
				o = fs_arpeggio()
				o.read(i)
				self.Arpeggios.append(o)

			if i.name == 'Song': 
				o = fs_song()
				o.read(i)
				self.Songs.append(o)

			if i.name == 'DPCMMapping': 
				o = dpcm_mapping()
				o.read(i)
				self.DPCMMappings.append(o)

	def write(self, block_obj):
		block_obj.name = 'Project'

		cmd_params = block_obj.attrib
		cmd_params['Version'] = self.Version
		cmd_params['TempoMode'] = self.TempoMode
		cmd_params['Name'] = self.Name
		cmd_params['Author'] = self.Author
		if self.Copyright: cmd_params['Copyright'] = self.Copyright
		if self.Expansions: cmd_params['Expansions'] = ','.join(self.Expansions)
		if self.NumN163Channels: cmd_params['NumN163Channels'] = self.NumN163Channels
		if self.VolumeDb != 0: cmd_params['VolumeDb'] = self.VolumeDb
		if self.VRC6VolumeDb != 0: cmd_params['VRC6VolumeDb'] = self.VRC6VolumeDb
		if self.VRC7VolumeDb != 0: cmd_params['VRC7VolumeDb'] = self.VRC7VolumeDb
		if self.FDSVolumeDb != 0: cmd_params['FDSVolumeDb'] = self.FDSVolumeDb
		if self.MMC5VolumeDb != 0: cmd_params['MMC5VolumeDb'] = self.MMC5VolumeDb
		if self.N163VolumeDb != 0: cmd_params['N163VolumeDb'] = self.N163VolumeDb
		if self.S5BVolumeDb != 0: cmd_params['S5BVolumeDb'] = self.S5BVolumeDb
		if self.EPSMVolumeDb != 0: cmd_params['EPSMVolumeDb'] = self.EPSMVolumeDb

		if self.EPSMTrebleDb != 0: cmd_params['EPSMTrebleDb'] = self.EPSMTrebleDb
		if self.EPSMTrebleRolloffHz >= 0: cmd_params['EPSMTrebleRolloffHz'] = self.EPSMTrebleRolloffHz
		if self.FDSTrebleDb != 0: cmd_params['FDSTrebleDb'] = self.FDSTrebleDb
		if self.FDSTrebleRolloffHz >= 0: cmd_params['FDSTrebleRolloffHz'] = self.FDSTrebleRolloffHz
		if self.MMC5TrebleDb != 0: cmd_params['MMC5TrebleDb'] = self.MMC5TrebleDb
		if self.MMC5TrebleRolloffHz >= 0: cmd_params['MMC5TrebleRolloffHz'] = self.MMC5TrebleRolloffHz
		if self.N163TrebleDb != 0: cmd_params['N163TrebleDb'] = self.N163TrebleDb
		if self.N163TrebleRolloffHz >= 0: cmd_params['N163TrebleRolloffHz'] = self.N163TrebleRolloffHz
		if self.S5BTrebleDb != 0: cmd_params['S5BTrebleDb'] = self.S5BTrebleDb
		if self.S5BTrebleRolloffHz >= 0: cmd_params['S5BTrebleRolloffHz'] = self.S5BTrebleRolloffHz
		if self.TrebleDb != 0: cmd_params['TrebleDb'] = self.TrebleDb
		if self.TrebleRolloffHz >= 0: cmd_params['TrebleRolloffHz'] = self.TrebleRolloffHz
		if self.VRC6TrebleDb != 0: cmd_params['VRC6TrebleDb'] = self.VRC6TrebleDb
		if self.VRC6TrebleRolloffHz >= 0: cmd_params['VRC6TrebleRolloffHz'] = self.VRC6TrebleRolloffHz
		if self.VRC7TrebleDb != 0: cmd_params['VRC7TrebleDb'] = self.VRC7TrebleDb
		if self.VRC7TrebleRolloffHz >= 0: cmd_params['VRC7TrebleRolloffHz'] = self.VRC7TrebleRolloffHz

		for x in self.DPCMSamples: x.write(block_obj.add_block('DPCMSample'))
		for x in self.DPCMMappings: x.write(block_obj.add_block('DPCMMapping'))
		for x in self.Instruments: x.write(block_obj.add_block('Instrument'))
		for x in self.Arpeggios: x.write(block_obj.add_block('Arpeggio'))
		for x in self.Songs: x.write(block_obj.add_block('Song'))

	def save_to_file(self, output_file):
		block_obj = famistudiotxt_block()
		self.write(block_obj)
		block_obj.save_to_file(output_file)

	def load_from_file(self, input_file):
		root_block = famistudiotxt_block()

		root_block.load_from_file(input_file)

		if DEBUG_IN_OUT:
			root_block.save_to_file('debug_in.txt')

		if root_block.name == 'Project':
			self.read(root_block)

		return True