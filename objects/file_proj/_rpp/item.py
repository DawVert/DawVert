from objects.file_proj._rpp import func as reaper_func
from objects.file_proj._rpp import source as rpp_source
from objects.file_proj._rpp import env as rpp_env
from objects.file_proj._rpp import fxchain as rpp_fxchain
import itertools

rvd = reaper_func.rpp_value
rvs = reaper_func.rpp_value.single_var
robj = reaper_func.rpp_obj

class rpp_item_take:
	def __init__(self):
		self.playrate = rvd([1,1,0,-1,0,0.0025], ['rate','preserve_pitch','pitch','stretch_mode','mode','fade_size'], None, True)
		self.volpan = rvd([1,0,1], None, None, True)
		self.name = rvs("", str, True)
		self.soffs = rvs(0.0, float, True)
		self.chanmode = rvs(0.0, float, True)
		self.guid = rvs("", str, True)
		self.source = None
		self.stretchmarks = None
		self.volenv = rpp_env.rpp_env()
		self.panenv = rpp_env.rpp_env()
		self.muteenv = rpp_env.rpp_env()
		self.pitchenv = rpp_env.rpp_env()
		self.selected = False
		self.takefx = None
		self.take_markers = []

	def write(self, rpp_data):
		self.name.write('NAME',rpp_data)
		self.volpan.write('TAKEVOLPAN', rpp_data)
		self.soffs.write('SOFFS',rpp_data)
		self.playrate.write('PLAYRATE', rpp_data)
		self.chanmode.write('CHANMODE',rpp_data)
		self.guid.write('GUID',rpp_data)

		if self.stretchmarks != None:
			out = []
			nummarks = len(self.stretchmarks)-1
			for n, sm in enumerate(self.stretchmarks):
				out += [str(x) for x in sm]
				if nummarks!=n: out += ['+']
			rpp_data.children.append(['SM']+out)

		for tkm in self.take_markers:
			rpp_data.children.append(['TKM']+tkm)

		if self.source != None:
			rpp_sourcedata = robj('SOURCE',[self.source.type])
			self.source.write(rpp_sourcedata)
			rpp_data.children.append(rpp_sourcedata)

		self.volenv.write('VOLENV', rpp_data)
		self.panenv.write('PANENV', rpp_data)
		self.muteenv.write('MUTEENV', rpp_data)
		self.pitchenv.write('PITCHENV', rpp_data)
		if self.takefx != None:
			rpp_fxchaindata = robj('TAKEFX',[])
			self.takefx.write(rpp_fxchaindata)
			rpp_data.children.append(rpp_fxchaindata)

class rpp_item:
	def __init__(self):
		self.fadein = rvd([1,0,0,1,0,0,0], ['fade_type','fade_time','num2','num3','num4','curve','num6'], None, True)
		self.fadeout = rvd([1,0,0,1,0,0,0], ['fade_type','fade_time','num2','num3','num4','curve','num6'], None, True)
		self.mute = rvd([0,0], ['mute','num1'], None, True)
		self.volpan = rvd([1,0,1,-1], ['vol','pan','vol2','panlaw'], None, True)
		self.playrate = rvd([1,1,0,-1,0,0.0025], ['rate','preserve_pitch','pitch','stretch_mode','mode','fade_size'], None, True)
		self.position = rvs(0.0, float, True)
		self.snapoffs = rvs(0.0, float, True)
		self.length = rvs(5.0, float, True)
		self.loop = rvs(0.0, float, True)
		self.alltakes = rvs(0.0, float, True)
		self.sel = rvs(0.0, float, True)
		self.iguid = rvs("", str, True)
		self.iid = rvs(2.0, float, True)
		self.name = rvs("", str, True)
		self.soffs = rvs(0.0, float, True)
		self.chanmode = rvs(0.0, float, True)
		self.color = rvs(0, int, False)
		self.guid = rvs("", str, True)
		self.source = None
		self.beat = rvs(1, int, True)
		self.stretchmarks = None
		self.group = rvs(0, int, False)
		self.lock = rvs(0, int, False)
		self.volenv = rpp_env.rpp_env()
		self.panenv = rpp_env.rpp_env()
		self.muteenv = rpp_env.rpp_env()
		self.pitchenv = rpp_env.rpp_env()
		self.takefx = None
		self.take_markers = []
		self.extra_takes = []

	def load(self, rpp_data):
		take_mode = self
		for name, is_dir, values, inside_dat in reaper_func.iter_rpp(rpp_data):
			if name == 'POSITION': self.position.set(values[0])
			if name == 'SNAPOFFS': self.snapoffs.set(values[0])
			if name == 'LENGTH': self.length.set(values[0])
			if name == 'LOOP': self.loop.set(values[0])
			if name == 'ALLTAKES': self.alltakes.set(values[0])
			if name == 'FADEIN': self.fadein.read(values)
			if name == 'FADEOUT': self.fadeout.read(values)
			if name == 'MUTE': self.mute.read(values)
			if name == 'SEL': self.sel.set(values[0])
			if name == 'IGUID': self.iguid.set(values[0])
			if name == 'IID': self.iid.set(values[0])
			if name == 'NAME': take_mode.name.set(values[0])
			if name == 'VOLPAN': self.volpan.read(values)
			if name == 'SOFFS': take_mode.soffs.set(values[0])
			if name == 'PLAYRATE': take_mode.playrate.read(values)
			if name == 'CHANMODE': take_mode.chanmode.set(values[0])
			if name == 'BEAT': self.beat.set(values[0])
			if name == 'GUID': take_mode.guid.set(values[0])
			if name == 'COLOR': self.color.set(values[0])
			if name == 'GROUP': self.group.set(values[0])
			if name == 'LOCK': self.lock.set(values[0])
			if name == 'VOLENV': take_mode.volenv.read(inside_dat, values)
			if name == 'PANENV': take_mode.panenv.read(inside_dat, values)
			if name == 'MUTEENV': take_mode.muteenv.read(inside_dat, values)
			if name == 'PITCHENV': take_mode.pitchenv.read(inside_dat, values)
			if name == 'TAKEVOLPAN': take_mode.volpan.read(values)
			if name == 'SM': 
				stretchmarks = [list(y) for x, y in itertools.groupby(values, lambda z: z == '+') if not x]
				take_mode.stretchmarks = [[float(z) for z in x] for x in stretchmarks]
			if name == 'SOURCE': 
				source_obj = rpp_source.rpp_source()
				source_obj.type = values[0]
				source_obj.load(inside_dat)
				take_mode.source = source_obj
			if name == 'TAKE': 
				take = rpp_item_take()
				if values:
					if values[0] == 'SEL': self.take = True
				take_mode = take
				self.extra_takes.append(take)
			if name == 'TAKEFX': 
				fxchain_obj = rpp_fxchain.rpp_fxchain()
				fxchain_obj.load(inside_dat)
				take_mode.takefx = fxchain_obj
			if name == 'TKM': 
				take_mode.take_markers.append(values)

	def write(self, rpp_data):
		self.position.write('POSITION',rpp_data)
		self.snapoffs.write('SNAPOFFS',rpp_data)
		self.length.write('LENGTH',rpp_data)
		self.loop.write('LOOP',rpp_data)
		self.alltakes.write('ALLTAKES',rpp_data)
		self.fadein.write('FADEIN', rpp_data)
		self.fadeout.write('FADEOUT', rpp_data)
		self.mute.write('MUTE', rpp_data)
		if self.beat.values[0] != 1: self.beat.write('BEAT',rpp_data)
		self.lock.write('LOCK', rpp_data)
		self.sel.write('SEL',rpp_data)
		self.group.write('GROUP', rpp_data)
		self.iguid.write('IGUID',rpp_data)
		self.iid.write('IID',rpp_data)
		self.name.write('NAME',rpp_data)
		self.color.write('COLOR',rpp_data)
		self.volpan.write('VOLPAN', rpp_data)
		self.soffs.write('SOFFS',rpp_data)
		self.playrate.write('PLAYRATE', rpp_data)
		self.chanmode.write('CHANMODE',rpp_data)
		self.guid.write('GUID',rpp_data)
		self.volenv.write('VOLENV', rpp_data)
		self.panenv.write('PANENV', rpp_data)
		self.muteenv.write('MUTEENV', rpp_data)
		self.pitchenv.write('PITCHENV', rpp_data)

		if self.stretchmarks != None:
			out = []
			nummarks = len(self.stretchmarks)-1
			for n, sm in enumerate(self.stretchmarks):
				out += [str(x) for x in sm]
				if nummarks!=n: out += ['+']

			rpp_data.children.append(['SM']+out)

		for tkm in self.take_markers:
			rpp_data.children.append(['TKM']+tkm)

		if self.source != None:
			rpp_sourcedata = robj('SOURCE',[self.source.type])
			self.source.write(rpp_sourcedata)
			rpp_data.children.append(rpp_sourcedata)

		if self.takefx != None:
			rpp_fxchaindata = robj('TAKEFX',[])
			self.takefx.write(rpp_fxchaindata)
			rpp_data.children.append(rpp_fxchaindata)

		for take in self.extra_takes:
			rpp_data.children.append('TAKE SEL' if take.selected else 'TAKE')
			take.write(rpp_data)