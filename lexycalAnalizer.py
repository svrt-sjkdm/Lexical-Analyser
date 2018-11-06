import re    # Modulo de expresiones regulares
import os    # Modulo para determinar si un archivo esta vacio 
import sys   # Modulo para paso de argumentos por la terminal

class Token(object):
	"""Token class"""
	def __init__(self, name, value):
		self.name = name
		self.value = value

'''
Lexeme -> Lexema a convertir en token
Class -> Clase a la que pertenece el lexema
'''
def createToken(Lexeme, Class):
	if Class == 0 or Class == 1 or Class == 7:                 # Lexemas que se introducen en la tabla de simbolos
		if Lexeme in symbolTable:					           # Si el lexema se encuentra en la tabla de simbolos
			token = Token(Class, symbolTable.index(Lexeme))    # Solo introducirlo en la tabla de tokens
			tokens.append(token)
		else:										           # Si no se encuentra en la tabla de simbolos
			token = Token(Class, len(symbolTable))             # Crear el token
			tokens.append(token)							   # Insertarlo en la tabla de tokens
			symbolTable.append(Lexeme)                         # Introducirlo en la tabla de simbolos
	else:											           # Lexemas que no se introducen en la tabla de simbolos
		token = Token(Class, Lexeme)                           # Creacion del token
		tokens.append(token)						           # Agregarlo a la tabla de tokens

reservedWords = ["auto", "const", "int", "short", "struct", "unsigned", "double", "float",
				 "break", "continue", "long", "signed", "switch", "void", "else", "for",
				 "case", "default", "register", "sizeof", "typedef", "volatile", "enum", "goto",
				 "char", "do", "return", "static", "union", "while", "extern", "if"]
artihmeticOp = ["+", "-", "*", "/", "=", "%", "**", "+=", "-=", "*=", "++", "--"]
logicOp = ["&&", "||", "~"]
relationOp = [">", "<", "<=", ">=", "=="]
specialSymbol = "\{|\}|\(|\)|\[|]|\,|\\;"
identifier = "\_+(_|0-9|[A-Za-z])*|[A-Za-z]([A-Za-z]|[0-9]|\_)*"

tmp = ""              # Cadena vacia para concatenar los caracteres leidos
words = []            # Lista para guardar los lexemas
tokens = []           # Lista para guardar los tokens
symbolTable = []      # Tabla de simbolos implementada como una lista
lines = 0             # Numero de lineas del programa fuente

tokensf = open('tokens.txt', 'w')        # Archivo para almacenar los tokens
symbolf = open('symbol_table.txt', 'w')  # Archivo para almacenar la tabla de simbolos

f = open(sys.argv[1], 'r')               # Objeto f para leer el archivo
char = f.read(1)                         # El 1 indica que solo se lee un caracter del archivo

# Analisis lexico 
while char:

	if re.match('\n', char):                # Salto de linea
		lines += 1

	elif re.match('\s|\t', char):           # Espacio o tabulador
		pass

	elif char == '"':                       # Cadenas (CLASE 7)
		tmp += char
		char = f.read(1)
		while char != '"':                  # Mientras no sea la comilla que cierra
			if re.match('\n|;', char):      # Si encuentra salto de linea, se produce un error
				print("\nError en linea %s: Necesitas cerrar la cadena" % str(lines+1))
				break
			else:
				tmp += char
				char = f.read(1)
		tmp += char 
		if '\n' in tmp:                     # Incrementa el numero de lineas si se produce el error
			lines += 1
		else:
			words.append(tmp)               
			createToken(tmp, 7)             # Crear token    

	elif re.match(specialSymbol, char):     # Simbolo especial (CLASE 8)
		words.append(char)               
		createToken(char, 8)				# Crear token
	elif char in relationOp:                # Operador relacional (CLASE 6)
		tmp += char
		last_position = f.tell()          
		char = f.read(1)
		if  char in relationOp:             # Si es un operador que consiste en mas de un caracter
			tmp += char
		else:
			f.seek(last_position)
		words.append(tmp)                   
		createToken(tmp, 6)  				# Crear token

	elif re.match("&|\||~", char):          # Operador logico (CLASE 5)
		tmp += char
		if char == '&':
			last_position = f.tell()
			char = f.read(1)
			if char == '&':
				tmp += char
				words.append(tmp)
				createToken(tmp, 5)         # Crear token
			else:
				print("\nError en linea %s : Operador no valido" % str(lines+1))
				f.seek(last_position)
		elif char == '|':
			last_position = f.tell()
			char = f.read(1)
			if char == '|':
				tmp += char
				words.append(tmp)
				createToken(tmp, 5)         # Crear token
			else:
				print("\nError en linea %s : Operador no valido" % str(lines+1))
				f.seek(last_position)
		else:
			words.append(tmp)
			createToken(tmp, 5)             # Crear token

	elif re.match('/', char):               # Comentarios u operador aritmetico '/'
		last_position = f.tell() 
		char = f.read(1)                 # Lee siguiente caracter para determinar que tipo de comentario es
		if re.match('/', char):             # Comentario simple
			while char:                     # Recorre el cursor hasta encontrar salto o fin de linea
				if char == '\n':
					break
				char = f.read(1)
			lines += 1
		elif re.match('\*', char):          # Comentario multi-linea
			error_line = lines+1            # En caso de producirse un error, guarda la linea donde se genera
			while char:                      
				char = f.read(1)     
				if char == '*':           
					char = f.read(1)
					if char == '/':         # Encuentra fin del comentario multi-linea
						break
				elif char == '\n':
					lines += 1
			if char == '':                  # Si no lo encuentra, se produce un error
				print('\nERROR LINEA %s: No cerraste el comentario multi-linea' % str(error_line))
		else:                               # Encuentra al caracter '/' el cual es un operador aritmetico
			words.append('/')
			createToken(tmp, 4)             # Crear token
			f.seek(last_position)

	elif re.match('(\+|-)?(0|(0?|[1-9][0-9]*)\.[0-9]*|[1-9][0-9]*)', char):   # Numeros reales 
		while re.match('(0|(0?|[1-9][0-9]*)\.[0-9]*|[1-9][0-9]*)', char):
			last_position = f.tell()
			tmp += char
			char = f.read(1)
		words.append(tmp)
		if '.' in tmp:
			createToken(tmp, 3)             # Crea token para numero real (CLASE 3)
		else :
			createToken(tmp, 2)             # Crea token para numero entero (CLASE 2)
		f.seek(last_position)

	elif char in artihmeticOp:              # Operador aritmetico (CLASE 4)
		tmp += char 
		last_position = f.tell() 
		char = f.read(1)
		if char in artihmeticOp:
			tmp += char		
		else:
			f.seek(last_position)
		words.append(tmp)                   
		createToken(tmp, 4)                 # Crear token

	elif re.match(identifier, char):        # Identificador o Palabra reservada  
		tmp += char 
		last_position = f.tell()    
		char = f.read(1)
		while re.match(identifier, char):
			tmp += char
			last_position = f.tell()
			char = f.read(1)
		words.append(tmp)
		if tmp in reservedWords:
			createToken(tmp, 0)         # Es una palabra reservada
		else:
			createToken(tmp, 1)         # Es un identificador
		f.seek(last_position)

	elif char == '#':					    # Libreria o macro
		while char:
			if char == '\n':
				lines += 1
				break
			char = f.read(1)
	else:
		print('\nError en linea %s: Operador no valido' % str(lines+1))

	tmp = ""
	char = f.read(1)

f.close()

if os.stat(sys.argv[1]).st_size == 0:      # Archivo vacio
	print('\nEl archivo esta vacio')
else:
	lines += 1
	print('\nINFORMACION DEL PROGRAMA:')
	print("\nNumero de lineas -> %s\n" % lines)
	print('----------Lexemes----------')
	for word in words:
		if word in reservedWords:
			print("Reserved Word : ", word)
		elif word in artihmeticOp:
			print("Arithmetic Operator : ", word)
		elif word in logicOp:
			print("Logic Operator : ", word)
		elif word in relationOp:
			print("Relational operator : ", word)
		elif re.match(identifier, word):
			print("Identifier : ", word)
		elif re.match(specialSymbol, word):
			print("Special Symbol : ", word)
		elif re.match('(\+|-)?(0?\.[0-9]*|[1-9][0-9]*\.[0-9]*)', word):
			print("Float number : ", word)
		elif re.match('((\+|-)?[1-9][0-9]*|0)', word):
			print("Integer number : ", word)
		elif re.match('\".*\"', word):
			print("String : ", word)
		else:
			print("No match found...")
	print('---------------------------')

	print('--------Symbol Table-------')
	for index,lexeme in enumerate(symbolTable):
		print(index, lexeme)
		symbolf.write('(' + str(index) + ', ' + str(lexeme) + ')' + '\n')
	print('---------------------------')

	print('----------Tokens-----------')
	for token in tokens:
		print('<%s, %s>' % (token.name, token.value))
		tokensf.write('<%s, %s>\n' % (token.name, token.value))
	print('---------------------------')
