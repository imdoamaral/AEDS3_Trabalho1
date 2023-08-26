# NOTA: Como no PDF do trabalho há um exemplo de saída onde aparentemente o grafo é não direcionado (isto é, a aresta X > Y só é contada uma vez),
# mas no email enviado o grafo é direcionado, preferi fazer as duas versões e solicitar o usuário qual versão ele prefere que seja usada, e adicionei a informação "-direcionado" # ou "-nao-direcionado" no nome do arquivo exportado.
# 
# A paginação foi implementada, visto que a API só retorna 200 resultados por vez. Para contornar isso, utilizei a própria API, que já retorna qual é a primeira e a última página de resultados no final da resposta do JSON.
# 
# Apenas votos iguais em um mesmo ID de votação ('Sim', 'Não' ou 'Abstenção') na coluna 'voto' são contabilizados como arestas.
# Os resultados são classificados por ordem alfabética.
# 
# Lib necessária: pip install requests
# 

import requests
import json

# Função para obter o número da última página
def obter_ultima_pagina(url):
    try:
        # Fazemos uma solicitação GET para o url
        print(f"Conectando a {url} para obter a última página.")
        resposta = requests.get(url)
        # Verificamos se a resposta foi bem sucedida
        # Esse método irá gerar uma exceção HTTPError se a resposta da solicitação HTTP tiver um status de erro (como 404, 500, etc.).
        resposta.raise_for_status()
        # Transformamos a resposta em formato JSON
        dados = json.loads(resposta.text)
        # Percorremos todos os links
        for link in dados['links']:
            # Quando encontramos o link para a última página
            if link['rel'] == 'last':
                last_page_url = link['href']
                # Extraímos o número da última página
                ultimo_numero_pagina = int(last_page_url.split('pagina=')[1].split('&')[0])
        return ultimo_numero_pagina
    except requests.HTTPError as e:
        print(f"Erro ao conectar a {url}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar a resposta JSON de {url}")
        return None

# Função para obter os votos das votações
def obter_votos(url_votacoes, base_url_votos, direcionado):
    # Obtemos o número da última página
    ultimo_numero_pagina = obter_ultima_pagina(url_votacoes)
    if ultimo_numero_pagina is None:
        print("Não foi possível obter o número da última página.")
        return None, None
    # Inicializamos os grafos e os votos
    grafo = {}
    votos = {}
    print(f"Obtendo todas a(s) {ultimo_numero_pagina} página(s) primeiro...")
    # Iteramos sobre todas as páginas
    for pagina in range(1, ultimo_numero_pagina + 1):
        print(f"Obtendo página {pagina}...")
        url_pagina = f"{url_votacoes}&pagina={pagina}"
        resposta = requests.get(url_pagina)
        dados = json.loads(resposta.text)
        # Iteramos sobre todas as votações na página
        for votacao in dados['dados']:
            id_votacao = votacao['id']
            print(f"Página {pagina}/{ultimo_numero_pagina}: Solicitando votos de {id_votacao}")
            url_votos = base_url_votos.format(ID=id_votacao)
            resposta = requests.get(url_votos)
            votos_data = json.loads(resposta.text)
            votos_deputados = {voto['deputado_']['nome'].replace(' ', '_'): voto['tipoVoto'] for voto in votos_data['dados']}
            # Iteramos sobre todos os deputados que votaram na votação
            for deputado, tipo_voto in votos_deputados.items():
                if deputado not in grafo:
                    grafo[deputado] = {}
                if deputado not in votos:
                    votos[deputado] = 0
                votos[deputado] += 1
                # Iteramos sobre todos os outros deputados
                for outro_deputado, outro_voto in votos_deputados.items():
                    # Se o outro deputado votou do mesmo jeito que o deputado atual e não é o mesmo deputado
                    if outro_voto == tipo_voto and outro_deputado != deputado:
                        if outro_deputado not in grafo[deputado]:
                            grafo[deputado][outro_deputado] = 0
                        # Incrementamos o peso da aresta entre o deputado e o outro deputado
                        grafo[deputado][outro_deputado] += 1
                        # Adiciona o voto ao outro deputado se o grafo não for direcionado
                        if not direcionado:
                            if outro_deputado not in grafo:
                                grafo[outro_deputado] = {}
                            if deputado not in grafo[outro_deputado]:
                                grafo[outro_deputado][deputado] = 0
                            grafo[outro_deputado][deputado] += 1


    return grafo, votos

def main():
    print("\nBem-vindo! Esse programa faz a análise de votações de deputados através da API da Câmara e gera dois arquivos que representam algumas relações de participação e votos em acordo.\n")
    data_inicio = input("Insira a data de início (Ex: 2023-01-01): ")
    orientacao = int(input("\nComo deseja representar os grafos?\nDigite 1 para Direcionado\nDigite 2 para Não-Direcionado\n________________________\n"))
    direcionado = orientacao == 1
    direcionado_str = 'direcionado' if direcionado else 'nao-direcionado'
    url_votacoes = f"https://dadosabertos.camara.leg.br/api/v2/votacoes?dataInicio={data_inicio}&ordem=DESC&ordenarPor=dataHoraRegistro"
    base_url_votos = "https://dadosabertos.camara.leg.br/api/v2/votacoes/{ID}/votos"
    grafo, votos = obter_votos(url_votacoes, base_url_votos, direcionado)
    if grafo is None or votos is None:
        print("Não foi possível obter os votos.")
        return
    with open(f'votacaoVotos-{data_inicio}-{direcionado_str}-graph.txt', 'w') as f:
        if direcionado:
            f.write(f"{len(grafo)} {sum(len(v) for v in grafo.values())}\n")
        else:
            f.write(f"{len(grafo)} {sum(len(v) for v in grafo.values())//2}\n")
        for deputado, arestas in grafo.items():
            for outro_deputado, peso in arestas.items():
                f.write(f"{deputado} {outro_deputado} {peso}\n")
    with open(f'votacaoVotos-{data_inicio}-{direcionado_str}-deputados.txt', 'w') as f:
        for deputado, num_votos in votos.items():
            f.write(f"{deputado} {num_votos}\n")
    print("Os grafos foram escritos nos arquivos:")
    print(f"- votacaoVotos-{data_inicio}-{direcionado_str}-graph.txt")
    print(f"- votacaoVotos-{data_inicio}-{direcionado_str}-deputados.txt")

if __name__ == "__main__":
    main()

