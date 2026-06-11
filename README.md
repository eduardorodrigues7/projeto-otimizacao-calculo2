# 💼 LucroMax — Maximização de Lucro Operacional

Projeto da disciplina **Resolução de Problemas Multivariáveis** — Cálculo 2  
Curso de Ciência da Computação · Centro Universitário do Pará (CESUPA)  
Professor: Pedro Girotto

## 👥 Equipe

| Nome | Matrícula |
|---|---|
| Bernardo Lins | 24070315 |
| Eduardo Rodrigues | 24070204 |

---

## 📌 Descrição

Aplicação full stack que resolve analiticamente o problema de **maximização de lucro** em duas linhas de produção, mantendo a mesma matemática do problema original.

A função objetivo é:

```
L(x, y) = a·x + b·y − c·x² − d·y² − e·x·y
```

onde `x` = unidades produzidas do Produto A e `y` = unidades produzidas do Produto B.

O sistema calcula:
- Derivadas parciais ∂L/∂x e ∂L/∂y
- Ponto crítico via ∇L = 0 (sistema 2×2)
- Classificação via Hessiana (máximo, mínimo ou ponto de sela)
- Análise de sensibilidade (variação ±10% nas receitas)
- Justificativa matemática passo a passo em linguagem acessível

---

## 👤 Persona

**Carla Martins**, 35 anos, gerente de produção em uma pequena fábrica de peças industriais.
Ela precisa decidir quanto produzir em duas linhas distintas para não perder lucro nem desperdiçar recursos.
**Dor:** usa decisões empíricas e não tem uma estratégia segura para maximizar o lucro operacional.
**Métrica de sucesso:** identificar a combinação de produção que gera o maior lucro possível.

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.10+
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/projeto-otimizacao-calculo2.git
cd projeto-otimizacao-calculo2

# 2. Instale as dependências
python -m pip install -r requirements.txt

# 3. Crie o banco de dados
python criar_banco.py

# 4. Inicie o servidor
python app.py
```

Acesse em: **http://localhost:5000**

---

## 💡 Exemplo de Uso

**Entrada:**

| Parâmetro | Valor |
|---|---|
| Receita do Produto A (a) | 1200 R$/unidade |
| Receita do Produto B (b) | 800 R$/unidade |
| Coeficiente de custo do Produto A (c) | 2 |
| Coeficiente de custo do Produto B (d) | 3 |
| Fator de interação (e) | 1 |

**Saída esperada:**

```json
{
  "x": 130.43,
  "y": 89.13,
  "lucro": 113913.04,
  "classificacao": "Máximo Global",
  "hessiana": { "h11": -4, "h12": -1, "h22": -6, "discriminante": 23.0 }
}
```

---

## 🗂️ Estrutura do Projeto

```
projeto-otimizacao-calculo2/
├── app.py           # Back end Flask — cálculo matemático completo
├── criar_banco.py   # Script de criação do banco SQLite
├── database.db      # Banco de dados (gerado ao rodar criar_banco.py)
├── index.html       # Front end
├── script.js        # Lógica do cliente
├── style.css        # Estilos
├── requirements.txt # Dependências Python
└── README.md        # Este arquivo
```

---

## 🤖 Nota

O projeto mantém a mesma abordagem matemática do problema original, apenas alterando o contexto para maximização de lucro em linhas de produção.

---