import ply.lex as lex

tokens = (
	'GROUP',
	'GROUP_START',
	'GROUP_END',
	'ATTRIB',
)

t_GROUP_START = r'\{'
t_GROUP_END = r'\}'
t_ignore  = ' \t'

def t_GROUP(t):
	r'\[(.*?)\]'
	t.value = t.value[1:-1]
	return t

def t_ATTRIB(t):
	r'.*\;'
	t.value = t.value[0:-1]
	splitv = t.value.split('=')
	if len(splitv)==2:
		splitv[0] = splitv[0].rstrip()
		splitv[1] = splitv[1].lstrip()
	t.value = splitv
	return t

def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

def t_error(t):
	print("Illegal character '%s'" % t.value[0])
	t.lexer.skip(1)

class zquence_group:
	def __init__(self):
		self.attrib = {}
		self.groups = []
		self.name = ''

	def __repr__(self):
		return '[zquence group: %s]' % self.name

	def __iter__(self):
		return self.groups.__iter__()

	def load_from_file(self, filename):
		f = open(filename)
		lexer = lex.lex()
		lexer.input(f.read())
		tok = lexer.token()
		return self.read(lexer)

	def read(self, lexer):
		firsttoken = lexer.token()
		if firsttoken.type=='GROUP_START':
			while True:
				ptoken = lexer.token()
				if ptoken is not None:
					if ptoken.type=='ATTRIB':
						attribval = ptoken.value
						if len(attribval)==2: self.attrib[attribval[0]] = attribval[1]
					elif ptoken.type=='GROUP':
						gname = ptoken.value
						ingroup = zquence_group()
						ingroup.name = gname
						ingroup.read(lexer)
						self.groups.append(ingroup)
					elif ptoken.type=='GROUP_END': break
				else: break
		return True

class zquence_song:
	def __init__(self):
		self.name = ''
		self.data = zquence_group()
		self.metadata = None
		self.mixers = None
		self.tracks = None
		self.patterns = None
		self.references = None
		self.globals = None

	def load_from_file(self, filename):
		f = open(filename)
		lexer = lex.lex()
		lexer.input(f.read())

		tok = lexer.token()
		if tok.type=='GROUP':
			self.name = tok.value
			self.data.read(lexer)

			founddata = {}
			for x in self.data:
				if x.name == 'MetaData': self.metadata = x
				if x.name == 'Mixers': self.mixers = x
				if x.name == 'Tracks': self.tracks = x
				if x.name == 'Patterns': self.patterns = x
				if x.name == 'References': self.references = x
				if x.name == 'Globals': self.globals = x
			return True
