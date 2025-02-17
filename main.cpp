#include <bits/stdc++.h>
using namespace std;

// For clarity, you might want to replace <bits/stdc++.h>
// with the specific includes you need:
// #include <iostream>
// #include <vector>
// #include <algorithm>
// #include <random>
// #include <fstream>
// #include <chrono>
// #include <cmath>
// #include <ctime>

////////////////////////////////////////////////////////////////////////////////
// Data structures
////////////////////////////////////////////////////////////////////////////////

struct Item {
    int valor;
    int peso;
};

struct Solucao {
    vector<int> vetor_solucao; // 0/1 for each item
    int peso_total;
    int valor_total;
};

struct Parametros {
    int quantidade_itens;
    int capacidade_mochila;
    int tamanho_populacao;
    int num_geracoes;
};

////////////////////////////////////////////////////////////////////////////////
// Utility: read items from file
////////////////////////////////////////////////////////////////////////////////

vector<Item> defineItens(const string &filename, int quantidade_itens) {
    // The function in Python:
    // 1) Skips the first line
    // 2) Reads the rest (value, weight)
    // 3) Returns a list/dict of items
    vector<Item> itens;
    itens.reserve(quantidade_itens);

    ifstream file(filename);
    if(!file.is_open()){
        cerr << "Erro ao abrir arquivo " << filename << endl;
        return itens;
    }

    // skip the first line
    string skipLine;
    if(!getline(file, skipLine)) {
        cerr << "Erro: arquivo sem conteudo na primeira linha." << endl;
        return itens;
    }

    // read the rest lines
    int i = 0;
    while(!file.eof()) {
        int valor, peso;
        file >> valor >> peso; 
        if(!file.fail()) {
            Item item;
            item.valor = valor;
            item.peso = peso;
            itens.push_back(item);
            i++;
            if(i >= quantidade_itens) break; 
        } else {
            // If the line is malformed, skip it
            file.clear();
            string dummy;
            getline(file, dummy);
        }
    }
    file.close();
    return itens;
}

////////////////////////////////////////////////////////////////////////////////
// Greedy solution
////////////////////////////////////////////////////////////////////////////////

vector<int> solucaoGulosa(const vector<Item> &itens, int capacidade_mochila, 
                          int &peso_total, int &valor_total) {
    // Sort items by ratio (value/peso) in descending order
    // We'll store indices to keep track
    vector<int> indices(itens.size());
    iota(indices.begin(), indices.end(), 0);

    sort(indices.begin(), indices.end(), [&](int a, int b){
        double r1 = double(itens[a].valor) / itens[a].peso;
        double r2 = double(itens[b].valor) / itens[b].peso;
        return r1 > r2;
    });

    vector<int> solucao(itens.size(), 0);
    peso_total  = 0;
    valor_total = 0;

    for(int idx : indices) {
        if(peso_total + itens[idx].peso <= capacidade_mochila) {
            solucao[idx] = 1;
            peso_total  += itens[idx].peso;
            valor_total += itens[idx].valor;
        }
    }
    printf("Solucao Gulosa Valor Total: %d\n", valor_total);
    return solucao;
}

////////////////////////////////////////////////////////////////////////////////
// Brute-force solution
////////////////////////////////////////////////////////////////////////////////

pair<vector<int>, int> solucaoForcaBruta(const vector<Item> &itens, int capacidade_mochila) {
    // We try all combinations from 0 to 2^n - 1
    // Keep track of the best combination
    int n = itens.size();
    long long limite = (1LL << n); // watch out for large n
    int melhor_valor = 0;
    vector<int> melhor_combinacao(n, 0);

    for(long long mask = 0; mask < limite; mask++) {
        int peso_total = 0;
        int valor_total = 0;
        for(int j = 0; j < n; j++) {
            if(mask & (1LL << j)) {
                peso_total  += itens[j].peso;
                valor_total += itens[j].valor;
            }
        }
        if(peso_total <= capacidade_mochila && valor_total > melhor_valor) {
            melhor_valor = valor_total;
            // Record combination
            for(int j=0; j<n; j++){
                melhor_combinacao[j] = (mask & (1LL << j)) ? 1 : 0;
            }
        }
    }
    // Return best combination and best value
    return {melhor_combinacao, melhor_valor};
}

////////////////////////////////////////////////////////////////////////////////
// Genetic Algorithm
////////////////////////////////////////////////////////////////////////////////

// Generates initial population, including one "greedy" solution
// (like the Python code: add the greedy solution in last position)

Solucao perturbaSolucao(const Solucao &base, const vector<Item>& itens, int capacidade_mochila, double taxaPerturbacao = 0.05) {
    Solucao nova = base;  // start from the greedy solution
    static mt19937 rng((unsigned)time(nullptr));
    uniform_real_distribution<double> dist(0.0, 1.0);

    // Perturb the solution: flip each bit with probability 'taxaPerturbacao'
    for (size_t i = 0; i < nova.vetor_solucao.size(); i++) {
        if (dist(rng) < taxaPerturbacao) {
            nova.vetor_solucao[i] = 1 - nova.vetor_solucao[i];
        }
    }
    
    // Recalculate peso_total and valor_total
    int peso_total = 0;
    int valor_total = 0;
    for (size_t i = 0; i < nova.vetor_solucao.size(); i++) {
        if (nova.vetor_solucao[i] == 1) {
            peso_total += itens[i].peso;
            valor_total += itens[i].valor;
        }
    }
    
    // Repair: if infeasible, remove random items until feasible
    while (peso_total > capacidade_mochila) {
        // Remove one random item that is currently selected
        vector<int> selected;
        for (size_t i = 0; i < nova.vetor_solucao.size(); i++) {
            if (nova.vetor_solucao[i] == 1)
                selected.push_back(i);
        }
        if (selected.empty()) break;  // safety check
        
        uniform_int_distribution<int> indexDist(0, selected.size()-1);
        int removeIndex = selected[indexDist(rng)];
        nova.vetor_solucao[removeIndex] = 0;
        peso_total -= itens[removeIndex].peso;
        valor_total -= itens[removeIndex].valor;
    }
    
    nova.peso_total = peso_total;
    nova.valor_total = valor_total;
    return nova;
}


vector<Solucao> geraPopulacaoInicial(const vector<Item> &itens, 
                                     int quantidade_itens, 
                                     int tamanho_populacao, 
                                     int capacidade_mochila) {
    static mt19937 rng((unsigned)time(nullptr)); 

    vector<Solucao> populacao(tamanho_populacao);

    Solucao greedy;
    int peso_g, valor_g;
    greedy.vetor_solucao = solucaoGulosa(itens, capacidade_mochila, peso_g, valor_g);
    greedy.peso_total  = peso_g;
    greedy.valor_total = valor_g;

    // Fill the population
    for (int j = 0; j < tamanho_populacao - 1; j++) {
        // Generate a perturbed version of the greedy solution
        Solucao s = perturbaSolucao(greedy, itens, capacidade_mochila, 0.05); // 5% perturbation rate
        populacao[j] = s;
    }

    


    // Optionally, add the pure greedy solution to ensure at least one high-quality individual
    populacao[tamanho_populacao - 1] = greedy;
    

    return populacao;
}

// Return the best (highest valor_total) solution from population
Solucao elitismo(const vector<Solucao> &populacao) {
    Solucao best = populacao[0];
    for(const auto &sol : populacao) {
        if(sol.valor_total > best.valor_total) {
            best = sol;
        }
    }
    return best;
}

// Tournament selection
Solucao torneio(const vector<Solucao> &populacao) {
    static mt19937 rng((unsigned)time(nullptr)); 
    uniform_int_distribution<int> dist(0, populacao.size()-1);

    int i1 = dist(rng);
    int i2 = dist(rng);

    if(populacao[i1].valor_total >= populacao[i2].valor_total) {
        return populacao[i1];
    } else {
        return populacao[i2];
    }
}

// One-point crossover
Solucao crossover(const Solucao &pai1, const Solucao &pai2) {
    static mt19937 rng((unsigned)time(nullptr)); 
    uniform_int_distribution<int> dist(1, pai1.vetor_solucao.size()-1);
    int ponto_crossover = dist(rng);

    Solucao filho;
    filho.vetor_solucao.resize(pai1.vetor_solucao.size());

    for(int i=0; i<ponto_crossover; i++){
        filho.vetor_solucao[i] = pai1.vetor_solucao[i];
    }
    for(int i=ponto_crossover; i<(int)pai1.vetor_solucao.size(); i++){
        filho.vetor_solucao[i] = pai2.vetor_solucao[i];
    }
    return filho;
}

// Mutation
Solucao mutacao(const Solucao &individuo_in, double taxa_mutacao=0.05) {
    static mt19937 rng((unsigned)time(nullptr)); 
    uniform_real_distribution<double> dist(0.0,1.0);

    Solucao individuo = individuo_in; // copy
    for(size_t i=0; i<individuo.vetor_solucao.size(); i++){
        if(dist(rng) < taxa_mutacao) {
            individuo.vetor_solucao[i] = 1 - individuo.vetor_solucao[i]; 
        }
    }
    return individuo;
}

// Evaluate the fitness of a solution
Solucao fitness(Solucao solucao, const vector<Item> &itens, int capacidade_mochila) {
    int peso_total = 0;
    int valor_total = 0;
    for(int i=0; i<(int)solucao.vetor_solucao.size(); i++){
        if(solucao.vetor_solucao[i] == 1){
            peso_total  += itens[i].peso;
            valor_total += itens[i].valor;
        }
    }
    if(peso_total > capacidade_mochila) {
        valor_total = 0; // penalize
    }
    solucao.peso_total  = peso_total;
    solucao.valor_total = valor_total;
    return solucao;
}

// Form the next generation
vector<Solucao> formaGeracao(const vector<Solucao> &populacao, 
                             int tamanho_populacao, 
                             const vector<Item> &itens,
                             int capacidade_mochila) 
{
    vector<Solucao> nova_geracao;
    nova_geracao.resize(tamanho_populacao);

    // Keep the best in position 0 (elitism)
    nova_geracao[0] = elitismo(populacao);

    int count = 1;
    while(count < tamanho_populacao) {
        Solucao pai1 = torneio(populacao);
        Solucao pai2 = torneio(populacao);

        static mt19937 rng((unsigned)time(nullptr)); 
        uniform_real_distribution<double> dist(0.0,1.0);
        double taxa_aleatoria_crossover = dist(rng);

        Solucao filho;
        if(taxa_aleatoria_crossover < 0.5) {
            filho = crossover(pai1, pai2);
        } else {
            // Clona pai1, se não houver crossover
            filho = pai1;
        }
        // Mutate
        filho = mutacao(filho, 0.05);

        // Fitness
        filho = fitness(filho, itens, capacidade_mochila);

        nova_geracao[count] = filho;
        count++;
    }
    return nova_geracao;
}

////////////////////////////////////////////////////////////////////////////////
// Main "mochila_binaria" logic
////////////////////////////////////////////////////////////////////////////////

void mochila_binaria(const Parametros &params, const string &filename) {
    using namespace std::chrono;

    // read items
    vector<Item> itens = defineItens(filename, params.quantidade_itens);
    auto start_total = high_resolution_clock::now();

    // generate initial population
    vector<Solucao> populacao = geraPopulacaoInicial(
        itens, 
        params.quantidade_itens, 
        params.tamanho_populacao, 
        params.capacidade_mochila
    );

    // For checking time
    auto end_pre = high_resolution_clock::now();
    auto elapsed_pre = duration_cast<milliseconds>(end_pre - start_total).count();
    cout << "Tempo de execucao (pre-loop): " << elapsed_pre/1000.0 << " s" << endl;

    // Genetic loop
    int estagnacao_count = 0;
    int melhor_valor_anterior = -1;
    vector<int> evolucao_melhores; 
    evolucao_melhores.reserve(params.num_geracoes);

    for(int g=0; g<params.num_geracoes; g++){
        // Create new generation
        populacao = formaGeracao(populacao, params.tamanho_populacao, itens, params.capacidade_mochila);

        // Evaluate best
        Solucao best = elitismo(populacao);
        evolucao_melhores.push_back(best.valor_total);

        // Check stagnation
        if(best.valor_total == melhor_valor_anterior) {
            estagnacao_count++;
        } else {
            estagnacao_count = 0;
        }
        melhor_valor_anterior = best.valor_total;

        if(estagnacao_count >= params.num_geracoes/5) {
            cout << "\nEstagnacao de melhoria por "<< params.num_geracoes/5 <<" geracoes. Encerrando...\n";
            break;
        }

    }

    Solucao melhor_final = elitismo(populacao);

    cout << "\n>>> Melhor Solucao Genetico: " << endl;
    cout << "Valor Total: " << melhor_final.valor_total << endl;
    // cout << "Peso Total:  " << melhor_final.peso_total << endl;

    auto end_total = high_resolution_clock::now();
    auto elapsed_total = duration_cast<milliseconds>(end_total - start_total).count();
    cout << "Tempo de execucao total: " << elapsed_total/1000.0 << " s" << endl;


    ofstream arquivo("c++_results.txt");
    if (arquivo.is_open()) {
        arquivo << "Geracao,MelhorValor\n";
        for (size_t i = 0; i < evolucao_melhores.size(); ++i) {
            arquivo << i + 1 << ":" << evolucao_melhores[i] << "\n";
        }
        arquivo.close();
        cout << "Resultados salvos em 'c++ results.txt'" << endl;
    } else {
        cerr << "Erro ao abrir o arquivo para escrita." << endl;
    }
    
}

////////////////////////////////////////////////////////////////////////////////
// main()
////////////////////////////////////////////////////////////////////////////////

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    //const string NOME_ARQUIVO = "2test.txt";
    const string NOME_ARQUIVO = "test_set/hardcore5000.txt";
    ifstream file(NOME_ARQUIVO);
    if(!file.is_open()) {
        cerr << "Erro ao abrir arquivo " << NOME_ARQUIVO << endl;
        return 1;
    }

    // Read first line: "quantidade_itens capacidade_mochila"
    Parametros params;
    file >> params.quantidade_itens >> params.capacidade_mochila;
    file.close();

    // Set genetic parameters
    params.tamanho_populacao = 200; // or any other you want
    params.num_geracoes      = 2000;

    cout << "Lido do arquivo: " << endl;
    cout << "Quantidade de Itens = " << params.quantidade_itens << endl;
    cout << "Capacidade da Mochila = " << params.capacidade_mochila << endl;

    // Run GA approach
    mochila_binaria(params, NOME_ARQUIVO);

    return 0;
}
