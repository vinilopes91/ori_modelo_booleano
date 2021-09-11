import nltk
import sys
import pickle
import os

def filtra_palavras_documentos(conteudo_arquivo):
    palavras = nltk.word_tokenize(conteudo_arquivo)
    palavras = list(filter(
        lambda word: word not in stopwords and word not in lista_caracteres, palavras))
    etiquetas = etiquetador_unigram.tag(palavras)
    palavras = [palavra[0] for palavra in etiquetas if palavra[1]
                not in lista_classes_stopwords]

    return palavras


def grava_indice(indice_invertido):
    with open('indice.txt', 'w') as reader:
        for radical in indice_invertido:
            line = ""
            for numero_arquivo in indice_invertido[radical]:
                line = line + \
                    f"{numero_arquivo},{indice_invertido[radical][numero_arquivo]} "
            reader.writelines(f"{radical}: {line}\n")

def grava_resultado_consulta(resultado_consulta):
    with open('resposta.txt', 'w') as reader:
        reader.writelines(f"{resultado_consulta['total']}\n")
        for nome_arquivo in resultado_consulta["arquivos"]:
            reader.writelines(f"{nome_arquivo}\n")

def busca_numero_arquivos_por_palavra(indice_invertido, stemmer, numero_arquivos, palavra):
    arquivos = set()

    if (palavra[0] == "!"):
        # documentos que não contem a palavra X
        radical = stemmer.stem(palavra[1:])
        contem_radical = set(list(indice_invertido[radical].keys()))
        arquivos = numero_arquivos - contem_radical
    else:
        # documentos que contem a palavra X
        radical = stemmer.stem(palavra)
        arquivos = set(list(indice_invertido[radical].keys()))

    return arquivos

def executa_consulta(consulta, indice_invertido, arquivos_base):
    stemmer = nltk.stem.RSLPStemmer()
    termos = consulta.split()
    numero_arquivos = set(range(1, len(arquivos_base) + 1))
    arquivos = set()

    if len(termos) == 1:
        palavra = termos[0]
        arquivos = busca_numero_arquivos_por_palavra(indice_invertido, stemmer, numero_arquivos, palavra)
    else:
        ## Conjunção
        for index, palavra_subconsulta in enumerate(termos):
            if (index % 2 == 0): # index par = palavras / index impar = conjunção
                if (index == 0):
                    arquivos = busca_numero_arquivos_por_palavra(indice_invertido, stemmer, numero_arquivos, palavra_subconsulta)
                else:
                    arquivos = arquivos.intersection(busca_numero_arquivos_por_palavra(indice_invertido, stemmer, numero_arquivos, palavra_subconsulta))

    return arquivos

if (len(sys.argv) <= 1):
    print('Arquivo base não encontrado')
    sys.exit()
elif (len(sys.argv) <= 2):
    print('consulta não encontrada')
    sys.exit()

# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('rslp')
# nltk.download('mac_morpho')

etiquetador_unigram = None

if (os.path.isfile('mac_morpho.pkl')):
    arquivo = open("mac_morpho.pkl", "rb")
    etiquetador_unigram = pickle.load(arquivo)
    arquivo.close()
else:
    sentencas_etiquetadas = nltk.corpus.mac_morpho.tagged_sents()
    etiq0 = nltk.DefaultTagger('N')
    etiquetador_unigram = nltk.UnigramTagger(
        sentencas_etiquetadas, backoff=etiq0)
    output = open('mac_morpho.pkl', 'wb')
    pickle.dump(etiquetador_unigram, output, -1)
    output.close()

# Lista de stopwords
stopwords = nltk.corpus.stopwords.words('portuguese')
# Extrator radicais
stemmer = nltk.stem.RSLPStemmer()

base = sys.argv[1]
arquivo_consulta = sys.argv[2]
consulta = None
subconsultas = []
arquivos_base = []
lista_classes_stopwords = ['PREP', 'KC', 'KS', 'ART']
lista_caracteres = ['.', '...', '..', ',', '!', '?']
indice_invertido = {}
resultado_consulta = {
    "total": 0,
    "arquivos": []
}

# Lê o arquivo de base e salva os arquivos a serem lidos
try:
    with open(base, 'r') as reader:
        arquivos_base = [file_name.strip() for file_name in reader.readlines()]
except EnvironmentError:
    print ("Arquivo base não encontrado.")
    sys.exit()

# Lê o arquivo_consulta
try:
    with open(arquivo_consulta, 'r') as reader:
        consulta = reader.readline().strip()
        subconsultas = consulta.split(" | ")
except EnvironmentError:
    print ("Arquivo consulta não encontrado.")
    sys.exit()

for file in arquivos_base:
    radicais_arquivo = {}
    numero_arquivo = arquivos_base.index(file) + 1

    try:
        with open(file, 'r') as reader:
            conteudo_arquivo = reader.read()
            palavras = filtra_palavras_documentos(conteudo_arquivo)
            for palavra in palavras:
                radical = stemmer.stem(palavra)
                if radical in radicais_arquivo:
                    radicais_arquivo[radical] += 1
                else:
                    radicais_arquivo[radical] = 1
    except EnvironmentError:
        print ("Arquivo %s não encontrado."%file)
        sys.exit()

    for radical in radicais_arquivo:
        if radical in indice_invertido:
            indice_invertido[radical][numero_arquivo] = radicais_arquivo[radical]
        else:
            indice_invertido[radical] = {
                numero_arquivo: radicais_arquivo[radical]}

grava_indice(indice_invertido)

resultado_numero_arquivos_consulta = set()

for consulta in subconsultas:
    conjunto_documentos = executa_consulta(consulta, indice_invertido, arquivos_base)
    resultado_numero_arquivos_consulta = resultado_numero_arquivos_consulta.union(conjunto_documentos)

resultado_consulta['total'] = len(resultado_numero_arquivos_consulta)

for numero_arquivo in resultado_numero_arquivos_consulta:
    resultado_consulta['arquivos'].append(arquivos_base[numero_arquivo - 1])

grava_resultado_consulta(resultado_consulta)
