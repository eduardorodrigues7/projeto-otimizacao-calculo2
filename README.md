# 🌿 AgroOtimiza — Otimização da Produção Agrícola

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

Aplicação full stack que resolve analiticamente o problema de **alocação ótima de área agrícola** entre duas culturas (açaí e mandioca), maximizando o lucro do produtor rural.

A função objetivo é:

```
L(x, y) = a·x + b·y − c·x² − d·y² − e·x·y
```

onde `x` = hectares de açaí, `y` = hectares de mandioca.

O sistema calcula:
- Derivadas parciais ∂L/∂x e ∂L/∂y
- Ponto crítico via ∇L = 0 (sistema 2×2)
- Classificação via Hessiana (máximo, mínimo ou ponto de sela)
- Análise de sensibilidade (variação ±10% nas receitas)
- Justificativa matemática passo a passo em linguagem acessível

---

## 👤 Persona

**Maria das Graças Souza**, 48 anos, produtora rural no município de Igarapé-Miri (PA).  
Cultiva açaí e mandioca há 20 anos de forma empírica, sem critério técnico para alocar as áreas.  
**Dor:** decide a divisão de área por intuição, frequentemente subalocando a cultura mais rentável.  
**Métrica de sucesso:** aumento de ≥ 15% no lucro anual após adotar a alocação recomendada pelo sistema.

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
pip install -r requirements.txt

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
| Receita do Açaí (a) | 1200 R$/ha |
| Receita da Mandioca (b) | 800 R$/ha |
| Custo quadrático açaí (c) | 2 |
| Custo quadrático mandioca (d) | 3 |
| Fator de competição (e) | 1 |

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

## 🤖 Uso de Inteligência Artificial

Este projeto utilizou **Claude (Anthropic)** como ferramenta de apoio para:
- Revisão e aprimoramento do código back end (cálculo das derivadas, hessiana e sensibilidade)
- Aprimoramento do front end (estrutura HTML, CSS e renderização dos passos matemáticos)
- Geração e revisão deste README

Todo o uso foi declarado conforme exigido pelas regras de integridade acadêmica do projeto.

---