import os
import pulp
import time

#NOME_ARQUIVO = "2test.txt"
NOME_ARQUIVO = "test_set/hardcore5000.txt"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import logging
logger = logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(funcName)s:%(message)s")
logger = logging.getLogger(__name__)

def read_knapsack_data(filename=NOME_ARQUIVO):
    """Reads the knapsack problem data from a file and returns capacity, number of items, weights, and values."""
    path = os.path.join(BASE_DIR, filename)
    capacity = 0
    number_of_items = 0
    weights = []
    values = []

    try:
        with open(path, "r") as file:
            # Read the first line to get number of items and capacity
            first_line = file.readline().strip().split()
            if len(first_line) != 2:
                print("Erro: Primeira linha inválida. Esperado: 'n capacidade'")
                return 0, 0, [], []

            number_of_items, capacity = map(int, first_line)

            # Read the rest of the file (values and weights)
            for line in file:
                parts = line.strip().split()
                if len(parts) != 2:
                    print(f"Erro no formato da linha: {line}")
                    continue

                value, weight = map(int, parts)  # Note: value comes first, then weight
                values.append(value)
                weights.append(weight)

        return capacity, number_of_items, weights, values

    except FileNotFoundError:
        print(f"Erro: O arquivo '{filename}' não foi encontrado.")
        return 0, 0, [], []

def solve_knapsack(filename=NOME_ARQUIVO):
    """Solves the 0/1 Knapsack Problem using PuLP (Single-Threaded Mode)."""
    # Read data
    capacity, num_items, weights, values = read_knapsack_data(filename)
    
    logger.debug(f"Data = Capacity: {capacity}, N_Items: {num_items}")
    logger.debug(f"Data = WEIGHTS: {weights}, VALUES: {values}")

    if num_items == 0:
        print("Nenhum item carregado.")
        return

    # Define the PuLP problem
    knapsack_problem = pulp.LpProblem("Knapsack_Problem", pulp.LpMaximize)

    # Define binary decision variables
    x = [pulp.LpVariable(f"x{i}", cat="Binary") for i in range(num_items)]

    # Objective function: maximize total value
    knapsack_problem += pulp.lpSum(values[i] * x[i] for i in range(num_items)), "Total Value"

    # Constraint: total weight must not exceed capacity
    knapsack_problem += pulp.lpSum(weights[i] * x[i] for i in range(num_items)) <= capacity, "Weight Constraint"

    # Solve the problem using CBC with single-thread mode
    solver = pulp.PULP_CBC_CMD(msg=True,threads=1)  # Ensuring single-thread execution
    #solver = pulp.GLPK_CMD(msg=True)  # Ensuring single-thread execution
    start_time = time.perf_counter()
    knapsack_problem.solve(solver)
    end_time = time.perf_counter()

    # Display results
    print("\n=== Resultado da Mochila Binária ===")
    print(f"Status: {pulp.LpStatus[knapsack_problem.status]}")
    print(f"Valor total máximo: {pulp.value(knapsack_problem.objective)}")
    print(f"Tempo decorrido (s): {end_time - start_time:.6f}")
    print("Itens selecionados:")

    selected_items = []
    for i in range(num_items):
        if pulp.value(x[i]) == 1:
            selected_items.append((i+1, weights[i], values[i]))
            logger.debug(f"Item {i+1}: Peso {weights[i]}, Valor {values[i]}")

    return selected_items

def main():
    solve_knapsack()


main()