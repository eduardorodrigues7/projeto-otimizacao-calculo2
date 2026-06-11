from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def conectar():
    return sqlite3.connect(os.path.join(BASE_DIR, "database.db"))


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

        a = float(dados["receita_acai"])
        b = float(dados["receita_mandioca"])
        c = float(dados["custo_acai"])
        d = float(dados["custo_mandioca"])
        e = float(dados["competencia"])

        if c <= 0 or d <= 0:
            return jsonify({"erro": "Os coeficientes de custo devem ser positivos."}), 400

        det_sistema = (2 * c) * (2 * d) - (e ** 2)

        if abs(det_sistema) < 1e-10:
            return jsonify({"erro": "Sistema sem solução única (determinante ≈ 0)."}), 400

        x_otimo = ((a * (2 * d)) - (b * e)) / det_sistema
        y_otimo = (((2 * c) * b) - (a * e)) / det_sistema

        if x_otimo < 0 or y_otimo < 0:
            return jsonify({
                "erro": "O ponto ótimo encontrado contém valores negativos, "
                        "o que não é viável para área cultivada. Revise os parâmetros.",
                "x": round(x_otimo, 4),
                "y": round(y_otimo, 4)
            }), 400

        lucro_otimo = (
            a * x_otimo + b * y_otimo
            - c * (x_otimo ** 2)
            - d * (y_otimo ** 2)
            - e * x_otimo * y_otimo
        )

        df_dx = a - 2 * c * x_otimo - e * y_otimo
        df_dy = b - e * x_otimo - 2 * d * y_otimo

        h11 = -2 * c
        h12 = -e
        h22 = -2 * d
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

        def lucro_de(a_, b_):
            x_ = ((a_ * (2 * d)) - (b_ * e)) / det_sistema
            y_ = (((2 * c) * b_) - (a_ * e)) / det_sistema
            return a_ * x_ + b_ * y_ - c * x_**2 - d * y_**2 - e * x_ * y_

        la10  = lucro_de(a * 1.1, b)
        la_10 = lucro_de(a * 0.9, b)
        lm10  = lucro_de(a, b * 1.1)
        lm_10 = lucro_de(a, b * 0.9)

        sensibilidade = {
            "receita_acai_mais10pct":      round(la10,  2),
            "receita_acai_menos10pct":     round(la_10, 2),
            "receita_mandioca_mais10pct":  round(lm10,  2),
            "receita_mandioca_menos10pct": round(lm_10, 2),
            "variacao_acai_mais10":   round(la10  - lucro_otimo, 2),
            "variacao_acai_menos10":  round(la_10 - lucro_otimo, 2),
            "variacao_mand_mais10":   round(lm10  - lucro_otimo, 2),
            "variacao_mand_menos10":  round(lm_10 - lucro_otimo, 2),
        }

        justificativa = (
            f"1. Função objetivo: L(x,y) = {a}x + {b}y - {c}x² - {d}y² - {e}xy\n\n"
            f"2. Derivadas parciais igualadas a zero (∇f = 0):\n"
            f"   ∂L/∂x = {a} - {2*c}x - {e}y = 0\n"
            f"   ∂L/∂y = {b} - {e}x - {2*d}y = 0\n\n"
            f"3. Resolução do sistema 2×2 (Regra de Cramer):\n"
            f"   Determinante = {round(det_sistema,4)}\n"
            f"   x* = {round(x_otimo,4)} ha  |  y* = {round(y_otimo,4)} ha\n\n"
            f"4. Hessiana:\n"
            f"   H = [ [{h11}, {h12}], [{h12}, {h22}] ]\n"
            f"   Discriminante D = {round(discriminante,4)}\n\n"
            f"5. Classificação: D > 0 e H₁₁ < 0 → {classificacao_resumo}\n\n"
            f"6. Lucro máximo: L({round(x_otimo,2)}, {round(y_otimo,2)}) = R$ {round(lucro_otimo,2)}\n\n"
            f"7. Sensibilidade: receita do açaí +10% → lucro de R$ {la10:.2f} "
            f"({'+' if la10-lucro_otimo>=0 else ''}{la10-lucro_otimo:.2f})"
        )

        conn = conectar()
        conn.execute("""
            INSERT INTO consultas (
                receita_acai, receita_mandioca, custo_acai, custo_mandioca,
                competencia, x_otimo, y_otimo, lucro, classificacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (a, b, c, d, e, x_otimo, y_otimo, lucro_otimo, classificacao))
        conn.commit()
        conn.close()

        return jsonify({
            "x": round(x_otimo, 4),
            "y": round(y_otimo, 4),
            "lucro": round(lucro_otimo, 2),
            "classificacao": classificacao,
            "derivadas": {
                "df_dx": f"{a} - {2*c}x - {e}y",
                "df_dy": f"{b} - {e}x - {2*d}y",
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
        SELECT id, receita_acai, receita_mandioca, x_otimo, y_otimo,
               lucro, classificacao, data_criacao
        FROM consultas ORDER BY data_criacao DESC LIMIT 10
    """)
    linhas = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": r[0], "receita_acai": r[1], "receita_mandioca": r[2],
         "x_otimo": round(r[3], 2), "y_otimo": round(r[4], 2),
         "lucro": round(r[5], 2), "classificacao": r[6], "data": r[7]}
        for r in linhas
    ])


if __name__ == "__main__":
    app.run(debug=True)