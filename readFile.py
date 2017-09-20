import re

class Token(object):
	"""Token class"""
	def __init__(self, name, value):
		self.name = name
		self.value = value


reservedWords = ["auto", "const", "int", "short", "struct", "unsigned", "double", "float",
				 "break", "continue", "long", "signed", "switch", "void", "else", "for",
				 "case", "default", "register", "sizeof", "typedef", "volatile", "enum", "goto",
				 "char", "do", "return", "static", "union", "while", "extern", "if"]
artihmeticOp = ["+", "-", "*", "/", "=", "%", "**", "+=", "-=", "*=", "++", "--"]
logicOp = ["&&", "||", "~"]
relationOp = [">", "<", "<=", ">=", "=="]
specialSymbol = "\{|\}|\(|\)|\[|\]"
identifier = "\_*[A-Z|a-z]+[\_|0-9|A-Za-z]*"

tmp = ""              # Cadena vacia para concatenar los caracteres leidos
words = []            # Lista para guardar los lexemas
tokens = []           # Lista para guardar los tokens
symbolTable = {}      # Tabla de simbolos implementada como un diccionario
lines = 0             # Numero de lineas del programa fuente

file = open('words.txt', 'r')
char = file.read(1)                         # El 1 indica que solo se lee un caracter del archivo

while char:
	if re.match('\n', char):
		if tmp                             # Si la cadena tmp no esta vacia
			words.append(tmp)
		lines += 1
		tmp = ""
	elif re.match('\s|\t', char):           # Cuando sea un espacio o tabulador
		if tmp:                             # Si la cadena tmp no esta vacia
			words.append(tmp)               # Crear token   
		tmp = ""
	elif char == '"':                       # Cuando encuentre una comilla que abre
		tmp += char
		char = file.read(1)
		while char != '"':                  # Mientras no sea la comilla que cierra
			if re.match('\n', char):        # Si encuentra salto de linea, se produce un error
				print("Error en linea %s: Necesitas cerrar la cadena" % str(lines+1))
				break
			else:
				tmp += char
				char = file.read(1)
		tmp += char 
		if '\n' in tmp:                     # Incrementa el numero de lineas si se produce el error
			lines += 1
			tmp = ""
		else:
			# Crear token
			words.append(tmp)
			tmp = ""
	else:
		tmp += char

	char = file.read(1)

file.close()

print(words)
print("Numero de lineas -> ", lines)

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