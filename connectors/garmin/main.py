"""
SCRIPT PRINCIPAL — Orquestrador do briefing diário
Execute este arquivo diretamente: python main.py
"""

import sys
import traceback
from datetime import date

def main():
    print(f"\n{'='*50}")
    print(f"  BRIEFING GARMIN — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    try:
        from coletar_dados import coletar
        print("📡 Coletando dados do Garmin Connect...")
        dados = coletar()

        if dados.get("erros"):
            print(f"⚠️  Alguns dados indisponíveis: {', '.join(dados['erros'])}")

        print("✅ Dados coletados com sucesso\n")

    except Exception as e:
        print(f"❌ Erro na coleta de dados: {e}")
        traceback.print_exc()
        sys.exit(1)

    try:
        from gerar_briefing import gerar_briefing, enviar_email
        print("🧠 Interpretando com Claude...")
        briefing = gerar_briefing(dados)

        print("\n" + "="*50)
        print(briefing)
        print("="*50 + "\n")

    except Exception as e:
        print(f"❌ Erro na geração do briefing: {e}")
        traceback.print_exc()
        sys.exit(1)

    try:
        hoje = date.today().strftime("%d/%m/%Y")
        assunto = f"🏃 Briefing Garmin — {hoje}"
        print("📧 Enviando por email...")
        enviar_email(assunto, briefing)

    except Exception as e:
        print(f"❌ Erro no envio do email: {e}")
        traceback.print_exc()
        sys.exit(1)

    print("\n✅ Briefing concluído com sucesso!")

if __name__ == "__main__":
    main()
