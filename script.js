async function calcular() {
  const erro = document.getElementById("erro");
  const resultado = document.getElementById("resultado");
  erro.style.display = "none";
  resultado.style.display = "none";

  const campos = {
    receita_alpha: document.getElementById("receitaAlpha").value,
    receita_beta: document.getElementById("receitaBeta").value,
    custo_alpha: document.getElementById("custoAlpha").value,
    custo_beta: document.getElementById("custoBeta").value,
    interacao: document.getElementById("interacao").value,
  };

  const labels = {
    receita_alpha: "receita do Produto A",
    receita_beta: "receita do Produto B",
    custo_alpha: "coeficiente de custo do Produto A",
    custo_beta: "coeficiente de custo do Produto B",
    interacao: "fator de interação entre produtos",
  };

  // Validação básica no front
  for (const [chave, val] of Object.entries(campos)) {
    if (val === "" || isNaN(Number(val))) {
      mostrarErro(`Preencha o campo "${labels[chave]}" com um número válido.`);
      return;
    }
  }

  const btn = document.querySelector(".btn-calcular");
  btn.textContent = "⏳ Calculando...";
  btn.disabled = true;

  try {
    const resposta = await fetch("/calcular", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(campos),
    });

    const dados = await resposta.json();

    if (dados.erro) {
      mostrarErro(dados.erro);
      return;
    }

    // ── Resultados principais ──────────────────────────────
    document.getElementById("res-x").textContent     = `${dados.x} unidades`;
    document.getElementById("res-y").textContent     = `${dados.y} unidades`;
    document.getElementById("res-lucro").textContent = `R$ ${dados.lucro.toLocaleString("pt-BR", {minimumFractionDigits:2})}`;
    document.getElementById("res-classif").textContent = dados.classificacao;

    // ── Cor da classificação ───────────────────────────────
    const classifEl = document.getElementById("res-classif");
    classifEl.className = "resultado-valor classificacao";
    if (dados.classificacao.includes("Máximo")) classifEl.classList.add("max");
    else if (dados.classificacao.includes("Mínimo")) classifEl.classList.add("min");
    else classifEl.classList.add("sela");

    // ── Tabela de sensibilidade ────────────────────────────
    const s = dados.sensibilidade;
    const linhas = [
      ["Receita do Produto A +10%", s.receita_alpha_mais10pct, s.variacao_alpha_mais10],
      ["Receita do Produto A −10%", s.receita_alpha_menos10pct, s.variacao_alpha_menos10],
      ["Receita do Produto B +10%", s.receita_beta_mais10pct,  s.variacao_beta_mais10],
      ["Receita do Produto B −10%", s.receita_beta_menos10pct,  s.variacao_beta_menos10],
    ];

    const tbody = document.getElementById("tabela-sens-body");
    tbody.innerHTML = linhas.map(([cenario, lucro, variacao]) => {
      const sinal = variacao >= 0 ? "+" : "";
      const cls   = variacao >= 0 ? "positivo" : "negativo";
      return `
        <tr>
          <td>${cenario}</td>
          <td>R$ ${lucro.toLocaleString("pt-BR",{minimumFractionDigits:2})}</td>
          <td class="${cls}">${sinal}R$ ${Math.abs(variacao).toLocaleString("pt-BR",{minimumFractionDigits:2})}</td>
        </tr>`;
    }).join("");

    // ── Justificativa matemática passo a passo ─────────────
    const d = dados;
    const steps = [
      {
        icone: "1️⃣",
        titulo: "Função Objetivo",
        texto: `Queremos maximizar o lucro total <strong>L(x, y)</strong>, onde
                <em>x</em> = unidades do Produto A e <em>y</em> = unidades do Produto B:`,
        formula: `L(x, y) = ${campos.receita_alpha}x + ${campos.receita_beta}y
− ${campos.custo_alpha}x² − ${campos.custo_beta}y² − ${campos.interacao}xy`,
      },
      {
        icone: "2️⃣",
        titulo: "Derivadas Parciais (∇L = 0)",
        texto: `Para encontrar o ponto de lucro máximo, calculamos as derivadas
                parciais em relação a <em>x</em> e <em>y</em> e as igualamos a zero:`,
        formula: `∂L/∂x = ${d.derivadas.df_dx} = 0\n∂L/∂y = ${d.derivadas.df_dy} = 0`,
      },
      {
        icone: "3️⃣",
        titulo: "Resolução do Sistema Linear",
        texto: `O sistema formado pelas duas equações acima é resolvido pela
                Regra de Cramer. O determinante da matriz de coeficientes é
                <strong>${d.hessiana.discriminante > 0 ? "diferente de zero" : "zero"}</strong>,
                garantindo solução única:`,
        formula: `x* = ${d.x} unidades  (Produto A)\ny* = ${d.y} unidades  (Produto B)`,
      },
      {
        icone: "4️⃣",
        titulo: "Verificação — Gradiente no Ponto Ótimo",
        texto: `Substituindo (x*, y*) nas derivadas parciais, confirmamos que o
                gradiente é ≈ 0 (condição de ponto crítico):`,
        formula: `∂L/∂x(${d.x}, ${d.y}) = ${d.derivadas.df_dx_no_ponto} ≈ 0 ✓\n∂L/∂y(${d.x}, ${d.y}) = ${d.derivadas.df_dy_no_ponto} ≈ 0 ✓`,
      },
      {
        icone: "5️⃣",
        titulo: "Matriz Hessiana e Classificação",
        texto: `A Hessiana avalia a curvatura da função no ponto crítico.
                Se o determinante <strong>D > 0 e H₁₁ < 0</strong>, o ponto é um máximo:`,
        formula: `H = | ${d.hessiana.h11}   ${d.hessiana.h12} |\n    | ${d.hessiana.h12}   ${d.hessiana.h22} |\n\nD = ${d.hessiana.h11} × ${d.hessiana.h22} − (${d.hessiana.h12})² = ${d.hessiana.discriminante}\n\n→ Classificação: ${d.classificacao}`,
      },
      {
        icone: "6️⃣",
        titulo: "Lucro Ótimo",
        texto: `Substituindo os valores ótimos na função objetivo:`,
        formula: `L(${d.x}, ${d.y}) = R$ ${d.lucro.toLocaleString("pt-BR",{minimumFractionDigits:2})}`,
      },
    ];

    document.getElementById("math-steps").innerHTML = steps.map(s => `
      <div class="math-step">
        <div class="step-header">
          <span class="step-icone">${s.icone}</span>
          <span class="step-titulo">${s.titulo}</span>
        </div>
        <p class="step-texto">${s.texto}</p>
        <pre class="step-formula">${s.formula}</pre>
      </div>
    `).join("");

    resultado.style.display = "block";
    resultado.scrollIntoView({ behavior: "smooth" });

  } catch (err) {
    mostrarErro("Não foi possível conectar ao servidor. Certifique-se de que o Flask está rodando.");
  } finally {
    btn.textContent = "📈 Calcular Produção Ótima";
    btn.disabled = false;
  }
}

function mostrarErro(msg) {
  const el = document.getElementById("erro");
  el.textContent = "⚠️ " + msg;
  el.style.display = "block";
}