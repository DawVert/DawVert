# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

def routetrackord(trackord, groupdata, outl, insidegroup):
	for t, i in trackord:
		outl.append([t, i, insidegroup])
		if i in groupdata:
			if t == 'GROUP': routetrackord(groupdata[i], groupdata, outl, i)

class groupassoc:
	def __init__(self):
		self.groupdata = []
		self.inside_found = []

	def add_part(self, groupname, insidegroup):
		for x in self.groupdata:
			if x[0] == groupname: 
				if insidegroup: 
					x[1] = insidegroup
					self.inside_found.append(x[1])
				return True
		self.groupdata.append([groupname, insidegroup])
		if insidegroup: 
			self.inside_found.append(insidegroup)
		return True

	def filter(self, insidegroup):
		for x in self.groupdata:
			if insidegroup == x[1]:
				yield x

	def iter(self, i):
		if i in self.inside_found or not i:
			for x in self.filter(i):
				yield x
				for d in self.iter(x[0]):
					yield d

class cvpj_groups:
	def __init__(self, convproj_obj):
		self.data = {}
		self.convproj_obj = convproj_obj

	def __getitem__(self, k):
		return self.data.__getitem__(k)

	def __contains__(self, k):
		return self.data.__contains__(k)

	def add(self, groupid):
		logger_project.info('Group - '+groupid)
		self.data[groupid] = tracks.cvpj_track('group', self.time_ppq, False, False)
		return self.data[groupid]

	def get(self, groupid):
		return self.data[groupid] if groupid in self.data else None

	def iter(self):
		for groupid, group_obj in self.data.items():
			yield groupid, group_obj

	def clear(self):
		self.data = {}

	def count_usage(self):
		groupcount = [x.group for _, x in self.data.items() if x.group != None]
		groupcount += [x.group for _, x in self.convproj_obj.tracks.data.items() if x.group != None]
		return list(Counter(groupcount))

	def remove_unused(self):
		groupcount = self.count_usage()
		unusedgroups = [x for x in list(self.data) if x not in groupcount]
		for x in unusedgroups: del self.data[x]

	def iter_inside(self):
		groups_assoc = groupassoc()

		for groupid, track_obj in self.iter():
			groups_assoc.add_part(groupid, track_obj.group)

		for groupid, insidegroup in groups_assoc.iter(None):
			yield groupid, insidegroup

	def iter_stream_inside(self):
		track_group = {}
		track_nongroup = []

		for groupid, group_obj in self.iter():
			if group_obj.group:
				if group_obj.group not in track_group: track_group[group_obj.group] = []
				track_group[group_obj.group].append(['GROUP', groupid])
			else: track_nongroup.append(['GROUP', groupid])

		for trackid, track_obj in self.convproj_obj.tracks.iter():
			if track_obj.group: 
				if track_obj.group not in track_group: track_group[track_obj.group] = []
				track_group[track_obj.group].append(['TRACK', trackid])
			else: track_nongroup.append(['TRACK', trackid])

		outl = []
		routetrackord(track_nongroup, track_group, outl, None)
		return outl
