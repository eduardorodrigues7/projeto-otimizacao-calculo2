async function calcular() {
  const erro = document.getElementById("erro");
  const resultado = document.getElementById("resultado");
  erro.style.display = "none";
  resultado.style.display = "none";

  const campos = {
    receita_acai:      document.getElementById("receitaAcai").value,
    receita_mandioca:  document.getElementById("receitaMandioca").value,
    custo_acai:        document.getElementById("custoAcai").value,
    custo_mandioca:    document.getElementById("custoMandioca").value,
    competencia:       document.getElementById("competencia").value,
  };

  // Validação básica no front
  for (const [chave, val] of Object.entries(campos)) {
    if (val === "" || isNaN(Number(val))) {
      mostrarErro(`Preencha o campo "${chave.replace(/_/g," ")}" com um número válido.`);
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
    document.getElementById("res-x").textContent     = `${dados.x} ha`;
    document.getElementById("res-y").textContent     = `${dados.y} ha`;
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
      ["Receita do Açaí +10%",     s.receita_acai_mais10pct,      s.variacao_acai_mais10],
      ["Receita do Açaí −10%",     s.receita_acai_menos10pct,     s.variacao_acai_menos10],
      ["Receita da Mandioca +10%", s.receita_mandioca_mais10pct,  s.variacao_mand_mais10],
      ["Receita da Mandioca −10%", s.receita_mandioca_menos10pct, s.variacao_mand_menos10],
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
                <em>x</em> = hectares de açaí e <em>y</em> = hectares de mandioca:`,
        formula: `L(x, y) = ${campos.receita_acai}x + ${campos.receita_mandioca}y
− ${campos.custo_acai}x² − ${campos.custo_mandioca}y² − ${campos.competencia}xy`,
      },
      {
        icone: "2️⃣",
        titulo: "Derivadas Parciais (∇f = 0)",
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
        formula: `x* = ${d.x} ha  (hectares de açaí)\ny* = ${d.y} ha  (hectares de mandioca)`,
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
    btn.textContent = "🌱 Calcular Produção Ótima";
    btn.disabled = false;
  }
}

function mostrarErro(msg) {
  const el = document.getElementById("erro");
  el.textContent = "⚠️ " + msg;
  el.style.display = "block";
}