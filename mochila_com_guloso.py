import random
import matplotlib.pyplot as plt
import os
import re 

import logging
import time

logger = logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(funcName)s: %(message)s")
logger = logging.getLogger(__name__)



NOME_ARQUIVO = "test_set/hardcore5000.txt"
print("Diretório atual:", os.getcwd())
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def define_itens_aleat(quantidade_itens):
  # Gera itens aleatorios 
  itens = {}
  for i in range(quantidade_itens):
    itens[i] = {}
    # peso de cada item varia de 1 até 20 kg
    itens[i]['peso'] = random.randint(1, 20)  
    # valor entre 10 e 100
    itens[i]['valor'] = random.randint(10, 100)
    #print(f"Item {i + 1}: {itens[i]}") 
    print(f"{itens[i]['peso']},{itens[i]['valor']}")
    
  return itens

def define_itens(quantidade_itens, nome_arquivo=NOME_ARQUIVO):
    path = os.path.join(BASE_DIR, NOME_ARQUIVO)
    print("Diretório do arquivo:", path)
    """Lê os itens do arquivo 'itens.txt' e retorna um dicionário sem o campo 'id'."""
    itens = {}
    try:
        with open(path, "r") as file:
            next(file)  # Skip the first line
            for i, linha in enumerate(file):
                partes = linha.strip().split()
                if len(partes) != 2:
                    print(f"Erro na linha {i + 1}: {linha} (Formato inválido, esperado: peso valor)")
                    continue
                
                valor, peso = map(int, partes)
                
                itens[i] = {
                    "valor": valor,
                    "peso": peso
                }

                logger.debug(f"Item {i + 1}: Valor = {valor}, Peso = {peso}")

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
    
    return itens

def solucao_gulosa(itens, capacidade_mochila):
    """Resolve o problema da mochila utilizando uma abordagem gulosa."""
    # Ordena os itens pelo valor por unidade de peso (razão valor/peso) de forma decrescente
   # Supondo que 'itens' seja um dicionário: {item_id: {'valor': ..., 'peso': ...}, ...}
    # Ordena os itens com base no valor/peso, mantendo os índices (chaves)
    itens_ordenados = sorted(itens.items(), key=lambda kv: kv[1]['valor'] / kv[1]['peso'], reverse=True)

    mochila_ids = set()
    peso_total = 0
    valor_total = 0

    for idx, item in itens_ordenados:
        if peso_total + item['peso'] <= capacidade_mochila:
            mochila_ids.add(idx)
            peso_total += item['peso']
            valor_total += item['valor']

    # Constrói o vetor solução usando os índices dos itens selecionados
    vetor_solucao = [1 if idx in mochila_ids else 0 for idx in itens.keys()]

    print(f"Solução Gulosa itens valor total: {valor_total}")#, {vetor_solucao}")
    #print("\nSolucao Gulosa itens:")
    # Printando vetor solucao
    #rint(vetor_solucao)
        
    #for i, item in enumerate(mochila):
        #print(f"Item{i}  - Peso: {item['peso']} kg, Valor: {item['valor']}")

    #print(f"Valor total: {valor_total}")
    #print(f"\nPeso total: {peso_total} kg")

    return vetor_solucao, peso_total, valor_total

def solucao_forca_bruta(itens, capacidade_mochila):
    """Resolve o problema da mochila utilizando força bruta."""
    melhor_valor = 0
    melhor_combinacao = []
    
    for i in range(2 ** len(itens)):
        combinacao = [int(x) for x in bin(i)[2:].zfill(len(itens))]
        peso_total = sum(itens[j]['peso'] * combinacao[j] for j in range(len(itens)))
        valor_total = sum(itens[j]['valor'] * combinacao[j] for j in range(len(itens)))
        
        if peso_total <= capacidade_mochila and valor_total > melhor_valor:
            melhor_valor = valor_total
            melhor_combinacao = combinacao

    logger.info("Solução Força Bruta:")
    logger.info(f"ÓTIMO: {melhor_valor}")#, combinacao: {melhor_combinacao}")

    return melhor_combinacao, melhor_valor

def gera_populacao_inicial(itens,quantidade_itens,tamanho_populacao,capacidade_mochila):
    # Gera um conjunto de soluções aleatórias
    populacao = {}

    for j in range(tamanho_populacao):
        vetor_solucao = [0] * quantidade_itens  # Inicializa solução vazia
        peso_total = 0
        valor_total = 0

        # Gera uma ordem aleatória dos itens para inserção
        indices = list(range(quantidade_itens))
        random.shuffle(indices)

        # Adiciona itens até atingir a capacidade da mochila
        for idx in indices:
            if peso_total + itens[idx]['peso'] <= capacidade_mochila:
                vetor_solucao[idx] = 1
                peso_total += itens[idx]['peso']

        # Calcula o valor total da solução
        valor_total = sum(itens[i]['valor'] for i in range(quantidade_itens) if vetor_solucao[i] == 1)

        # Salva a solução na população
        populacao[j] = {
            "vetor_solucao": vetor_solucao,
            "peso_total": peso_total,
            "valor_total": valor_total,
        }
    # adiciona a solução gulosa na ultima posição
    """ gul_vetor_solucao, gul_peso_total, gul_valor_total = solucao_gulosa(itens, capacidade_mochila)
    populacao[tamanho_populacao - 1] = {
            "vetor_solucao": gul_vetor_solucao,
            "peso_total": gul_peso_total,
            "valor_total": gul_valor_total,
        } """
        
    return populacao

def elitismo(populacao):
    return max(populacao.values(), key=lambda x: x["valor_total"])

def torneio(populacao):
    indice1, indice2 = random.sample(list(populacao.keys()), 2)
    individuo1 = populacao[indice1]
    individuo2 = populacao[indice2]
    if individuo1['valor_total'] >= individuo2['valor_total']:
        return individuo1
    else:
        return individuo2

def crossover(pai1, pai2):
    # crossover de 1 ponto
    ponto_crossover = random.randint(1, len(pai1["vetor_solucao"]) - 1)
    parte_do_pai1 = pai1["vetor_solucao"][:ponto_crossover]
    parte_do_pai2 = pai2["vetor_solucao"][ponto_crossover:]
    vetor_filhos = parte_do_pai1 + parte_do_pai2
    return {"vetor_solucao": vetor_filhos}

def mutacao(individuo, taxa_mutacao=0.05):
    novo_vetor = []
    # percorre cada gene do vetor solucao
    for gene in individuo["vetor_solucao"]:
        # se for menor que a taxa de mutação , faz a mutação
        if random.random() < taxa_mutacao:
            novo_vetor.append(1 - gene)  #inverte o bit
        else:
            novo_vetor.append(gene)  
    individuo["vetor_solucao"] = novo_vetor
    return individuo

def fitness(solucao, itens, capacidade_mochila):
    # Verifica o fitness dos filhos
    peso_total = sum(itens[i]["peso"] * solucao["vetor_solucao"][i] for i in range(len(itens)))
    valor_total = sum(itens[i]["valor"] * solucao["vetor_solucao"][i] for i in range(len(itens)))

    # Penalização: solução inválida recebe valor 0
    if peso_total > capacidade_mochila:
        valor_total = 0  
        #print("O carai")

    solucao["peso_total"] = peso_total
    solucao["valor_total"] = valor_total
    return solucao

def forma_geracao(populacao,tamanho_populacao,itens,capacidade_mochila):
    nova_geracao = {}
    nova_geracao[0] = elitismo(populacao) # escolhe o melhor individuo para proxima geracao
    # realiza crossover e gera filhos matando os pais, ate que forme uma nova geracao
    while len(nova_geracao) < tamanho_populacao:
        pai1 = torneio(populacao)
        pai2 = torneio(populacao)
        taxa_aleatoria_crossover = random.random()
        if taxa_aleatoria_crossover < 0.5:  
            filho = crossover(pai1, pai2)
        else:
            filho = {"vetor_solucao": pai1["vetor_solucao"][:]}  # Clona pai1 se não houver crossover

        filho = mutacao(filho, taxa_mutacao=0.05)

        filho = fitness(filho, itens, capacidade_mochila)

        nova_geracao[len(nova_geracao)] = filho  

    return nova_geracao

def plotar_grafico(evolucao):
    """ Plota um gráfico da evolução do valor máximo das gerações. """
    plt.plot(range(len(evolucao)), evolucao, marker='o', linestyle='-', color='b', label="Melhor Valor")
    plt.xlabel("Geração")
    plt.ylabel("Melhor Valor da População")
    plt.title("Evolução do Melhor Valor ao Longo das Gerações")
    plt.legend()
    plt.grid()
    plt.show()

def mochila_binaria(parametros):
    start_time = time.time()
    itens = define_itens(parametros['quantidade_itens'])
    populacao = gera_populacao_inicial(itens,parametros['quantidade_itens'],parametros['tamanho_populacao'],parametros['capacidade_mochila'])
    #nova_geracao = forma_geracao(populacao,parametros['tamanho_populacao'],itens,parametros['capacidade_mochila'])
    evolucao_melhores = []  
    melhor_valor_anterior = 0  
    estagnacao_count = 0  
    end = time.time()
    elapsed = end - start_time
    print(f"Tempo de execução: para começar{elapsed:.6f} segundos")
    

    start_time = time.time()

    for geracao in range(parametros['num_geracoes']):
        populacao = forma_geracao(populacao, parametros['tamanho_populacao'], itens, parametros['capacidade_mochila'])
        melhor_valor = elitismo(populacao)['valor_total']
        evolucao_melhores.append(melhor_valor)

        logger.debug(f"\n>>> Geração {geracao + 1}: Melhor Valor = {melhor_valor}")

        # Critério de parada: Melhoria Estagnada
        if melhor_valor == melhor_valor_anterior:
            estagnacao_count += 1
        else:
            estagnacao_count = 0  # Reseta se houve melhoria

        melhor_valor_anterior = melhor_valor

        if estagnacao_count >= parametros['num_geracoes']/5:
            print(f"\n Melhoria estagnada por {parametros['num_geracoes']/5} gerações. Algoritmo encerrado.")
            break

    melhor_final = elitismo(populacao)
    logger.info("\n>>> Melhor Solução Genético:")
    logger.info(f"Valor Total: {melhor_final['valor_total']}")
    logger.debug(f"Peso Total: {melhor_final['peso_total']}")
    #logger.info(f"Vetor Solução: \n{melhor_final['vetor_solucao']}, tamanho = {len(melhor_final['vetor_solucao'])}")
    end = time.time()
    elapsed = end - start_time
    print(f"Tempo de execução: {elapsed:.6f} segundos")
    #plotar_grafico(evolucao_melhores)
    start = time.time()
    solucao_gulosa(itens, parametros['capacidade_mochila'])
    end = time.time()
    elapsed = end - start
    print(f"Tempo de execução gulosa: {elapsed:.6f} segundos")
    start = time.time()
    #solucao_forca_bruta(itens, parametros['capacidade_mochila'])
    #end = time.time()
    #elapsed = end - start
    #print(f"Tempo de execução forca bruta: {elapsed:.6f} segundos")
    #plotar_grafico(evolucao_melhores)

def main():
    parametros = {}
    # 1 1 4
    nome_arquivo = NOME_ARQUIVO
    path = os.path.join(BASE_DIR, nome_arquivo)
    try:
        with open(path, "r") as file:
            linha = file.readline()
            partes = linha.strip().split()
            parametros["quantidade_itens"] = int(partes[0])
            parametros["capacidade_mochila"] = int(partes[1])

    except FileNotFoundError:
        print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado.")
        return

    parametros["tamanho_populacao"] = 200
    parametros["num_geracoes"] = 2000
    print(parametros)
    mochila_binaria(parametros)

main()
