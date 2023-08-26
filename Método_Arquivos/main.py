# NOTA: Como no PDF do trabalho há um exemplo de saída onde aparentemente o grafo é não direcionado (isto é, a aresta X > Y só é contada uma vez),
# mas no email enviado o grafo é direcionado, preferi fazer as duas versões e solicitar o usuário qual versão ele prefere que seja usada, e adicionei a informação "-direcionado"
# ou "-nao-direcionado" no nome do arquivo exportado.
# 
# Apenas votos iguais em um mesmo ID de votação ('Sim', 'Não' ou 'Abstenção') na coluna 'voto' são contabilizados como arestas.
# Os resultados são classificados por ordem alfabética.
# 
# Lib necessária: pip install pandas
#


import pandas as pd
import os

# Função para construir o grafo
def construir_grafo(df):
    grafo = {}
    deputado_votos = {}

    # Iterar por cada linha do dataframe
    for index, row in df.iterrows():
        id_votacao = row['idVotacao']
        voto = row['voto']
        deputado_id = row['deputado_id']
        deputado_nome = row['deputado_nome'].replace(' ', '_')  # substituir espaços por underscore

        # Adicionando votos ao deputado_votos
        if deputado_nome not in deputado_votos:
            deputado_votos[deputado_nome] = 1
        else:
            deputado_votos[deputado_nome] += 1

        # Verificar se a votação já está no grafo
        if id_votacao not in grafo:
            grafo[id_votacao] = {}

        # Adicionar o voto do deputado ao grafo
        if voto in grafo[id_votacao]:
            grafo[id_votacao][voto].append(deputado_nome)
        else:
            grafo[id_votacao][voto] = [deputado_nome]

    return grafo, deputado_votos

# Função para calcular a concordância entre deputados
def calcular_concordancia(grafo, direcionado):
    concordancia = {}

    # Iterar por cada votação no grafo
    for votacao in grafo.values():
        # Iterar por cada tipo de voto na votação
        for votos in votacao.values():
            # Iterar por cada combinação de deputados que votaram da mesma maneira
            for i in range(len(votos)):
                for j in range(i+1, len(votos)):
                    par_deputados = (votos[i], votos[j])  # Criar um par ordenado
                    par_deputados_invertido = (votos[j], votos[i])  # Criar o par inverso

                    # Adicionar concordância ao dicionário
                    if par_deputados not in concordancia:
                        concordancia[par_deputados] = 1
                    else:
                        concordancia[par_deputados] += 1

                    # Adicionar concordância do par inverso ao dicionário se for direcionado
                    if direcionado:
                        if par_deputados_invertido not in concordancia:
                            concordancia[par_deputados_invertido] = 1
                        else:
                            concordancia[par_deputados_invertido] += 1

    return concordancia

# Função para escrever os resultados em arquivos de texto
def escrever_resultados(concordancia, deputado_votos, nome_base, direcionado):
    # Arquivos de saida com parte do nome do arquivo de entrada
    tipo = "-direcionado" if direcionado else "-nao-direcionado"
    nome_arquivo_grafo = f"{nome_base}{tipo}-graph.txt"
    nome_arquivo_deputados = f"{nome_base}{tipo}-deputados.txt"

    # Escrever concordância no arquivo de grafo
    with open(nome_arquivo_grafo, 'w') as f:
        f.write(f"{len(deputado_votos)} {len(concordancia)}\n")
        for par_deputados, concord in concordancia.items():
            f.write(f"{par_deputados[0]} {par_deputados[1]} {concord}\n")

    # Escrever votos de deputados no arquivo de deputados
    with open(nome_arquivo_deputados, 'w') as f:
        for deputado, votos in deputado_votos.items():
            f.write(f"{deputado} {votos}\n")

    return nome_arquivo_grafo, nome_arquivo_deputados

def main():
    print("\nBem-vindo! Esse programa faz a análise de votações de deputados através da escolha de um arquivo Excel e gera dois arquivos que representam algumas relações de participação e votos em acordo.\n")
    nome_arquivo_entrada = input("Informe o nome do arquivo: ")

    # Pergunta ao usuário sobre o tipo de grafo
    tipo_grafo = input("\nComo deseja representar os grafos?\nDigite 1 para Direcionado\nDigite 2 para Não-Direcionado\n________________________\n")

    # Ler o arquivo Excel em um dataframe pandas
    df = pd.read_excel(nome_arquivo_entrada)

    # Filtrar apenas as linhas que possuem voto igual a 'Sim', 'Não' ou 'Abstenção'
    df = df[df['voto'].isin(['Sim', 'Não', 'Abstenção'])]

    # Construir o grafo
    grafo, deputado_votos = construir_grafo(df)

    # Verifica se o usuário escolheu grafo direcionado ou não
    direcionado = True if tipo_grafo == "1" else False

    # Calcular a concordância entre os deputados
    concordancia = calcular_concordancia(grafo, direcionado)

    # Nome base é a parte do nome do arquivo de entrada antes do ponto
    nome_base = os.path.splitext(os.path.basename(nome_arquivo_entrada))[0]

    # Escrever os resultados nos arquivos de texto
    nome_arquivo_grafo, nome_arquivo_deputados = escrever_resultados(concordancia, deputado_votos, nome_base, direcionado)

    print(f"Os grafos foram escritos nos arquivos:\n- {nome_arquivo_grafo}\n- {nome_arquivo_deputados}")

if __name__ == "__main__":
    main()

