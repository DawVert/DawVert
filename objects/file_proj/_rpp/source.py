from objects.file_proj._rpp import func as reaper_func

robj = reaper_func.rpp_obj
rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var

class rpp_source:
	def __init__(self):
		self.type = 'NONE'
		self.length = rvs('', float, False)
		self.mode = rvs(0, int, False)
		self.file = rvs('', str, False)
		self.startpos = rvs('', float, False)
		self.overlap = rvs('', float, False)
		self.hasdata = rvd([0,960,'QN'], ['hasdata', 'ppq', 'ppq_l'], [bool,int,str], False)
		self.transpose = rvs(0, int, False)
		self.notes = []
		self.source = None
		self.ccinterp = rvs(0, int, False)
		self.filter = rvs(0, int, False)
		self.outch = rvs(0, int, False)
		self.chase_cc_takeoffs = rvs(1, int, False)
		self.guid = rvs("", str, True)
		self.igntempo = rvd([0,120,4,4], ['on', 'bpm', 'ts_num', 'ts_denom'], [int,float,int,int], False)
		self.srccolor = rvs(1, int, False)
		self.vellane = rvd([-1,100,0,0,1], None, [int,int,int,int,int], False)

	def load(self, rpp_data):
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'FILE': self.file.set(values[0])
			elif name == 'E': self.notes.append([True]+values)
			elif name == 'e': self.notes.append([False]+values)
			elif name == 'HASDATA': self.hasdata.read(values)
			elif name == 'LENGTH': self.length.read(values)
			elif name == 'STARTPOS': self.startpos.read(values)
			elif name == 'OVERLAP': self.overlap.read(values)
			elif name == 'MODE': self.mode.read(values)
			elif name == 'TRANSPOSE': self.transpose.read(values)
			elif name == 'SOURCE': 
				source_obj = rpp_source()
				source_obj.type = values[0]
				source_obj.load(inside_dat)
				self.source = source_obj
			elif name == 'CCINTERP': self.ccinterp.read(values)
			elif name == 'FILTER': self.filter.read(values)
			elif name == 'OUTCH': self.outch.read(values)
			elif name == 'CHASE_CC_TAKEOFFS': self.chase_cc_takeoffs.read(values)
			elif name == 'GUID': self.guid.read(values)
			elif name == 'IGNTEMPO': self.igntempo.read(values)
			elif name == 'SRCCOLOR': self.srccolor.read(values)
			elif name == 'VELLANE': self.vellane.read(values)

	def write(self, rpp_data):
		self.length.write('LENGTH', rpp_data)
		self.mode.write('MODE', rpp_data)
		self.file.write('FILE', rpp_data)
		self.startpos.write('STARTPOS', rpp_data)
		self.overlap.write('OVERLAP', rpp_data)
		self.hasdata.write('HASDATA', rpp_data)
		for note in self.notes: 
			rpp_data.children.append(['E' if note[0] else 'e']+note[1:])
		self.ccinterp.write('CCINTERP', rpp_data)
		if self.transpose.get(): self.transpose.write('TRANSPOSE', rpp_data)
		if self.source:
			rpp_sourcedata = robj('SOURCE',[self.source.type])
			self.source.write(rpp_sourcedata)
			rpp_data.children.append(rpp_sourcedata)
		self.filter.write('FILTER', rpp_data)
		self.outch.write('OUTCH', rpp_data)
		self.chase_cc_takeoffs.write('CHASE_CC_TAKEOFFS', rpp_data)
		self.guid.write('GUID',rpp_data)
		self.igntempo.write('IGNTEMPO',rpp_data)
		self.srccolor.write('SRCCOLOR',rpp_data)
		self.vellane.write('VELLANE',rpp_data)