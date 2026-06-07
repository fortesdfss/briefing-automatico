"""
SCRIPT PRINCIPAL — Orquestrador do briefing diário com histórico
"""

import sys
import traceback
from datetime import date

def main():
    print(f"\n{'='*50}")
    print(f"  BRIEFING GARMIN — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    # ETAPA 1 — Coletar dados
    try:
        from coletar_dados import coletar
        print("Coletando dados do Garmin Connect...")
        dados = coletar()
        if dados.get("erros"):
            print(f"Avisos: {', '.join(dados['erros'])}")
        print("Dados coletados\n")
    except Exception as e:
        print(f"Erro na coleta: {e}")
        traceback.print_exc()
        sys.exit(1)

    # ETAPA 2 — Salvar histórico
    try:
        from historico import salvar, comparar
        salvar(dados)
        print("Gerando comparacoes historicas...")
        comparacoes = comparar(dados)
        print(f"Periodos com dados: {[k for k, v in comparacoes.items() if v.get('n', 0) > 0]}\n")
    except Exception as e:
        print(f"Aviso no historico: {e}")
        comparacoes = {}

    # ETAPA 3 — Gerar briefing
    try:
        from gerar_briefing import gerar_briefing, enviar_email
        print("Interpretando com Claude...")
        briefing = gerar_briefing(dados, comparacoes)
        print("\n" + "="*50)
        print(briefing)
        print("="*50 + "\n")
    except Exception as e:
        print(f"Erro no briefing: {e}")
        traceback.print_exc()
        sys.exit(1)

    # ETAPA 4 — Enviar email
    try:
        hoje = date.today().strftime("%d/%m/%Y")
        assunto = f"Briefing Garmin — {hoje}"
        print("Enviando email...")
        enviar_email(assunto, briefing)
        print("Concluido!")
    except Exception as e:
        print(f"Erro no email: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
