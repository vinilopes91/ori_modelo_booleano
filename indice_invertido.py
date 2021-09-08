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
            reader.writelines(f"{radical}: {indice_invertido[radical]}\n")


if (len(sys.argv) <= 1):
    print('Arquivo base não encontrado')
    sys.exit()

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('rslp')
nltk.download('mac_morpho')

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
arquivos_base = []
indice_invertido = {}
lista_classes_stopwords = ['PREP', 'KC', 'KS', 'ART']
lista_caracteres = ['.', '...', '..', ',', '!', '?']

# Lê o arquivo de base e salva os arquivos a serem lidos
with open(sys.argv[1], 'r') as reader:
    arquivos_base = [file_name.strip() for file_name in reader.readlines()]

for file in arquivos_base:
    radicais_arquivo = {}
    numero_arquivo = arquivos_base.index(file) + 1

    with open(file, 'r') as reader:
        conteudo_arquivo = reader.read()
        palavras = filtra_palavras_documentos(conteudo_arquivo)
        for palavra in palavras:
            radical = stemmer.stem(palavra)
            if radical in radicais_arquivo:
                radicais_arquivo[radical] += 1
            else:
                radicais_arquivo[radical] = 1

    for radical in radicais_arquivo:
        if radical in indice_invertido:
            indice_invertido[radical] = indice_invertido[radical] + \
                f"{numero_arquivo},{radicais_arquivo[radical]} "
        else:
            indice_invertido[radical] = f"{numero_arquivo},{radicais_arquivo[radical]} "

grava_indice(indice_invertido)
