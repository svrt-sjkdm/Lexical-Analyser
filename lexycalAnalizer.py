import re      # Modulo de expresiones regulares
import os      # Modulo para determinar si un archivo esta vacio 
import sys     # Modulo para paso de argumentos por la terminal
import codecs  # Modulo para leer en formato Unicode

class Token(object):
	"""Token class"""
	def __init__(self, name, value):
		self.name = name
		self.value = value

'''
Lexeme -> Lexema a convertir en token
Class ->  Clase a la que pertenece el lexema
'''
def createToken(Lexeme, Class):
	if Class == 0 or Class == 1 or Class == 7:                     # Lexemas que se introducen en la tabla de simbolos
		if Lexeme in symbolTable:					               # Si el lexema se encuentra en la tabla de simbolos
			token = Token(Class, symbolTable.index(Lexeme))        # Solo introducirlo en la tabla de tokens
			tokens.append(token)
			tokensFile.write('%s %s\n' % (token.name, token.value))# Escribir token en archivo
		else:										               # Si no se encuentra en la tabla de simbolos
			token = Token(Class, len(symbolTable))                 # Crear el token
			tokens.append(token)							       # Insertarlo en la tabla de tokens
			symbolTable.append(Lexeme)                             # Introducirlo en la tabla de simbolos
			symbolFile.write('%s %s\n' % (token.value, Lexeme))     
			tokensFile.write('%s %s\n' % (token.name, token.value))
	else:											               # Lexemas que no se introducen en la tabla de simbolos
		token = Token(Class, Lexeme)                               # Creacion del token
		tokens.append(token)						               # Agregarlo a la tabla de tokens
		tokensFile.write('%s %s\n' % (token.name, token.value))         


reservedWords = ["auto", "konst", "ganzezahl", "kurz", "struktur", "unsigniert", "doppelt", "schweben",
				 "unterbrechung", "fortsetzen", "lange", "signiert", "schalter", "leere", "sonst", "fur",
				 "fall", "foreinstellung", "registrierung", "grossevon", "typedefinieren", "fluchtig", "aufzahlung", "goto",
				 "verkohlen", "machen", "ruckkehr", "statisch", "union", "solange", "externe", "wenn"]
artihmeticOp = ["+", "-", "*", "/", "=", "%", "**", "+=", "-=", "*=", "++", "--"]
logicOp = ["&&", "||", "~"]
relationOp = [">", "<", "<=", ">=", "=="]
specialSymbol = "\{|\}|\(|\)|\[|]|\,|\\;"
identifier = "\_+(_|0-9|[A-Za-zäöüÄÖÜß])*|[A-Za-zäöüÄÖÜß]([A-Za-zäöüÄÖÜß]|[0-9]|\_)*"

tmp = ""              # Cadena vacia para concatenar los caracteres leidos
tokens = []           # Lista para guardar los tokens
symbolTable = []      # Tabla de simbolos implementada como una lista
lines = 0             # Numero de lineas del programa fuente

tokensFile = open('tokens.txt', 'w')                            # Archivo para almacenar los tokens
symbolFile = open('symbol_table.txt', 'w')                      # Archivo para almacenar la tabla de simbolos

file = codecs.open(sys.argv[1], encoding='utf-8')               # Objeto file para leer el archivo
char = file.read(1)                                             # El 1 indica que solo se lee un caracter del archivo

# Analisis lexico 
while char:

	if re.match('\n', char):                # Salto de linea
		lines += 1

	elif re.match('\s|\t', char):           # Espacio o tabulador
		pass

	elif char == '"':                       # Cadenas (CLASE 7)
		tmp += char
		char = file.read(1)
		while char != '"':                  # Mientras no sea la comilla que cierra
			if re.match('\n|;', char):      # Si encuentra salto de linea, se produce un error
				print("\nError en linea %s: Necesitas cerrar la cadena." % str(lines+1))
				break
			else:
				tmp += char
				char = file.read(1)
		tmp += char 
		if '\n' in tmp:                     # Incrementa el numero de lineas si se produce el error
			lines += 1
		else:          
			createToken(tmp, 7)             # Crear token    

	elif re.match(specialSymbol, char):     # Simbolo especial (CLASE 8)        
		createToken(char, 8)				# Crear token
	elif char in relationOp:                # Operador relacional (CLASE 6)
		tmp += char
		last_position = file.tell()          
		char = file.read(1)
		if  char in relationOp:             # Si es un operador que consiste en mas de un caracter
			tmp += char
		else:
			file.seek(last_position)                  
		createToken(tmp, 6)  				# Crear token

	elif re.match("&|\||~", char):          # Operador logico (CLASE 5)
		tmp += char
		if char == '&':
			last_position = file.tell()
			char = file.read(1)
			if char == '&':
				tmp += char
				createToken(tmp, 5)         # Crear token
			else:
				print("\nError en linea %s : Operador no valido." % str(lines+1))
				file.seek(last_position)
		elif char == '|':
			last_position = file.tell()
			char = file.read(1)
			if char == '|':
				tmp += char
				createToken(tmp, 5)         # Crear token
			else:
				print("\nError en linea %s : Operador no valido." % str(lines+1))
				file.seek(last_position)
		else:
			createToken(tmp, 5)             # Crear token

	elif re.match('/', char):               # Comentarios u operador aritmetico '/'
		last_position = file.tell() 
		char = file.read(1)                 # Lee siguiente caracter para determinar que tipo de comentario es
		if re.match('/', char):             # Comentario simple
			while char:                     # Recorre el cursor hasta encontrar salto o fin de linea
				if char == '\n':
					break
				char = file.read(1)
			lines += 1
		elif re.match('\*', char):          # Comentario multi-linea
			error_line = lines+1            # En caso de producirse un error, guarda la linea donde se genera
			while char:                      
				char = file.read(1)     
				if char == '*':           
					char = file.read(1)
					if char == '/':         # Encuentra fin del comentario multi-linea
						break
				elif char == '\n':
					lines += 1
			if char == '':                  # Si no lo encuentra, se produce un error
				print('\nError en la linea %s: No cerraste el comentario multi-linea.' % str(error_line))
		else:                               # Encuentra al caracter '/' el cual es un operador aritmetico
			createToken(tmp, 4)             # Crear token
			file.seek(last_position)

	elif re.match('(\+|-)?(0|(0?|[1-9][0-9]*)\.[0-9]*|[1-9][0-9]*)', char):   # Numeros reales 
		while re.match('(0|(0?|[1-9][0-9]*)\.[0-9]*|[1-9][0-9]*)', char):
			last_position = file.tell()
			tmp += char
			char = file.read(1)
		if '.' in tmp:
			createToken(tmp, 3)             # Crea token para numero real (CLASE 3)
		else :
			createToken(tmp, 2)             # Crea token para numero entero (CLASE 2)
		file.seek(last_position)

	elif char in artihmeticOp:              # Operador aritmetico (CLASE 4)
		tmp += char 
		last_position = file.tell() 
		char = file.read(1)
		if char in artihmeticOp:
			tmp += char		
		else:
			file.seek(last_position)                 
		createToken(tmp, 4)                 # Crear token

	elif re.match(identifier, char):        # Identificador o Palabra reservada  
		tmp += char 
		print('**** ', char)
		last_position = file.tell()    
		char = file.read(1)
		while re.match(identifier, char):
			tmp += char
			print('**** ', char)
			last_position = file.tell()
			char = file.read(1)
		if tmp in reservedWords:
			createToken(tmp, 0)             # Es una palabra reservada
		else:
			createToken(tmp, 1)             # Es un identificador
		file.seek(last_position)

	elif char == '#':					    # Libreria o macro
		while char:
			if char == '\n':
				lines += 1
				break
			char = file.read(1)
	else:
		print('\nError en linea %s: Operador no valido.' % str(lines+1))

	tmp = ""
	char = file.read(1)

file.close()

if os.stat(sys.argv[1]).st_size == 0:        # Archivo vacio
	print('\nEl archivo esta vacio')
else:
	lines += 1
	print('\nINFORMACION DEL PROGRAMA:')
	print("\nNumero de lineas -> %s\n" % lines)

	print('--------Symbol Table-------')
	for index,lexeme in enumerate(symbolTable):
		print(index, lexeme)
	print('---------------------------')

	print('----------Tokens-----------')
	for token in tokens:
		print('<%s, %s>' % (token.name, token.value))
	print('---------------------------')