from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def conectar():
    return sqlite3.connect(os.path.join(BASE_DIR, "database.db"))


def inicializar_banco():
    conn = conectar()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receita_alpha REAL,
            receita_beta REAL,
            custo_alpha REAL,
            custo_beta REAL,
            interacao REAL,
            x_otimo REAL,
            y_otimo REAL,
            lucro REAL,
            classificacao TEXT,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── Servir arquivos estáticos ─────────────────────────────
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route("/calcular", methods=["POST"])
def calcular():
    try:
        dados = request.json

        receita_alpha = float(dados["receita_alpha"])
        receita_beta = float(dados["receita_beta"])
        custo_alpha = float(dados["custo_alpha"])
        custo_beta = float(dados["custo_beta"])
        interacao = float(dados["interacao"])

        if custo_alpha <= 0 or custo_beta <= 0:
            return jsonify({"erro": "Os coeficientes de custo devem ser positivos."}), 400

        det_sistema = (2 * custo_alpha) * (2 * custo_beta) - (interacao ** 2)

        if abs(det_sistema) < 1e-10:
            return jsonify({"erro": "Sistema sem solução única (determinante ≈ 0)."}), 400

        x_otimo = ((receita_alpha * (2 * custo_beta)) - (receita_beta * interacao)) / det_sistema
        y_otimo = (((2 * custo_alpha) * receita_beta) - (receita_alpha * interacao)) / det_sistema

        if x_otimo < 0 or y_otimo < 0:
            return jsonify({
                "erro": "O ponto ótimo encontrado contém valores negativos, "
                        "o que não é viável para a produção. Revise os parâmetros.",
                "x": round(x_otimo, 4),
                "y": round(y_otimo, 4)
            }), 400

        lucro_otimo = (
            receita_alpha * x_otimo + receita_beta * y_otimo
            - custo_alpha * (x_otimo ** 2)
            - custo_beta * (y_otimo ** 2)
            - interacao * x_otimo * y_otimo
        )

        df_dx = receita_alpha - 2 * custo_alpha * x_otimo - interacao * y_otimo
        df_dy = receita_beta - interacao * x_otimo - 2 * custo_beta * y_otimo

        h11 = -2 * custo_alpha
        h12 = -interacao
        h22 = -2 * custo_beta
        discriminante = (h11 * h22) - (h12 ** 2)

        if discriminante > 0 and h11 < 0:
            classificacao = "Máximo Global"
            classificacao_resumo = "máximo global"
        elif discriminante > 0 and h11 > 0:
            classificacao = "Mínimo Global"
            classificacao_resumo = "mínimo global"
        elif discriminante < 0:
            classificacao = "Ponto de Sela"
            classificacao_resumo = "ponto de sela"
        else:
            classificacao = "Inconclusivo (D = 0)"
            classificacao_resumo = "inconclusivo"

        def lucro_de(r_alpha, r_beta):
            x_ = ((r_alpha * (2 * custo_beta)) - (r_beta * interacao)) / det_sistema
            y_ = (((2 * custo_alpha) * r_beta) - (r_alpha * interacao)) / det_sistema
            return r_alpha * x_ + r_beta * y_ - custo_alpha * x_**2 - custo_beta * y_**2 - interacao * x_ * y_

        la10  = lucro_de(receita_alpha * 1.1, receita_beta)
        la_10 = lucro_de(receita_alpha * 0.9, receita_beta)
        lb10  = lucro_de(receita_alpha, receita_beta * 1.1)
        lb_10 = lucro_de(receita_alpha, receita_beta * 0.9)

        sensibilidade = {
            "receita_alpha_mais10pct":      round(la10,  2),
            "receita_alpha_menos10pct":     round(la_10, 2),
            "receita_beta_mais10pct":       round(lb10,  2),
            "receita_beta_menos10pct":      round(lb_10, 2),
            "variacao_alpha_mais10":        round(la10  - lucro_otimo, 2),
            "variacao_alpha_menos10":       round(la_10 - lucro_otimo, 2),
            "variacao_beta_mais10":         round(lb10  - lucro_otimo, 2),
            "variacao_beta_menos10":        round(lb_10 - lucro_otimo, 2),
        }

        justificativa = (
            f"1. Função objetivo: L(x,y) = {receita_alpha}x + {receita_beta}y "
            f"- {custo_alpha}x² - {custo_beta}y² - {interacao}xy\n\n"
            f"2. Derivadas parciais igualadas a zero (∇L = 0):\n"
            f"   ∂L/∂x = {receita_alpha} - {2*custo_alpha}x - {interacao}y = 0\n"
            f"   ∂L/∂y = {receita_beta} - {interacao}x - {2*custo_beta}y = 0\n\n"
            f"3. Resolução do sistema 2×2 (Regra de Cramer):\n"
            f"   Determinante = {round(det_sistema,4)}\n"
            f"   x* = {round(x_otimo,4)} unidades  |  y* = {round(y_otimo,4)} unidades\n\n"
            f"4. Hessiana:\n"
            f"   H = [ [{h11}, {h12}], [{h12}, {h22}] ]\n"
            f"   Discriminante D = {round(discriminante,4)}\n\n"
            f"5. Classificação: D > 0 e H₁₁ < 0 → {classificacao_resumo}\n\n"
            f"6. Lucro máximo: L({round(x_otimo,2)}, {round(y_otimo,2)}) = R$ {round(lucro_otimo,2)}\n\n"
            f"7. Sensibilidade: receita do Produto A +10% → lucro de R$ {la10:.2f} "
            f"({'+' if la10-lucro_otimo>=0 else ''}{la10-lucro_otimo:.2f})"
        )

        conn = conectar()
        conn.execute("""
            INSERT INTO consultas (
                receita_alpha, receita_beta, custo_alpha, custo_beta,
                interacao, x_otimo, y_otimo, lucro, classificacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (receita_alpha, receita_beta, custo_alpha, custo_beta, interacao, x_otimo, y_otimo, lucro_otimo, classificacao))
        conn.commit()
        conn.close()

        return jsonify({
            "x": round(x_otimo, 4),
            "y": round(y_otimo, 4),
            "lucro": round(lucro_otimo, 2),
            "classificacao": classificacao,
            "derivadas": {
                "df_dx": f"{receita_alpha} - {2*custo_alpha}x - {interacao}y",
                "df_dy": f"{receita_beta} - {interacao}x - {2*custo_beta}y",
                "df_dx_no_ponto": round(df_dx, 8),
                "df_dy_no_ponto": round(df_dy, 8),
            },
            "hessiana": {
                "h11": h11, "h12": h12, "h22": h22,
                "discriminante": round(discriminante, 4),
            },
            "sensibilidade": sensibilidade,
            "justificativa": justificativa,
        })

    except KeyError as ke:
        return jsonify({"erro": f"Parâmetro ausente: {ke}"}), 400
    except ValueError:
        return jsonify({"erro": "Todos os campos devem ser números válidos."}), 400
    except Exception as erro:
        return jsonify({"erro": str(erro)}), 500


@app.route("/historico", methods=["GET"])
def historico():
    conn = conectar()
    cursor = conn.execute("""
        SELECT id, receita_alpha, receita_beta, x_otimo, y_otimo,
               lucro, classificacao, data_criacao
        FROM consultas ORDER BY data_criacao DESC LIMIT 10
    """)
    linhas = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "receita_alpha": r[1], "receita_beta": r[2],
         "x_otimo": round(r[3], 2), "y_otimo": round(r[4], 2),
         "lucro": round(r[5], 2), "classificacao": r[6], "data": r[7]}
        for r in linhas
    ])


inicializar_banco()

if __name__ == "__main__":
    app.run(debug=True)