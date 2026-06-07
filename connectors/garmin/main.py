"""
SCRIPT PRINCIPAL — Orquestrador do fisiologista diário
Fluxo: coleta -> treino segmentado -> intenção/carga -> histórico ->
       sinais longitudinais -> modelo carga-resposta -> interpretação -> email
"""

import sys
import traceback
from datetime import date, timedelta


def main():
    print(f"\n{'='*50}")
    print(f"  FISIOLOGISTA DIÁRIO — {date.today().strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")
    hoje = date.today()

    # 1 — Coleta diária
    try:
        from coletar_dados import coletar, conectar_garmin
        print("Coletando dados do Garmin...")
        client = conectar_garmin()
        dados = coletar(hoje=hoje, client=client)
        if dados.get("erros"):
            print(f"Avisos: {', '.join(dados['erros'])}")
        print("OK\n")
    except Exception as e:
        print(f"Erro na coleta: {e}"); traceback.print_exc(); sys.exit(1)

    # 2 — Treino segmentado por modalidade
    try:
        from treino_prescrito_executado import coletar_treino
        print("Analisando treinos do dia...")
        treino = coletar_treino(client, hoje)
        print(f"Modalidades: {treino.get('modalidades_do_dia')}\n")
    except Exception as e:
        print(f"Aviso treino: {e}")
        treino = {"prescrito": None, "atividades": [], "modalidades_do_dia": []}

    # 3 — Inferência de intenção e carga do dia
    try:
        from motor_intencao_resposta import carga_do_dia, modelo_carga_resposta
        carga = carga_do_dia(dados, treino)
        dados["_carga"] = carga
        print(f"Intenções inferidas: {carga.get('intencoes')} | peso carga: {carga.get('peso_carga_dia')}\n")
    except Exception as e:
        print(f"Aviso intenção: {e}")
        carga = {"intencoes": [], "peso_carga_dia": 0}

    # 4 — Carregar histórico (antes de salvar hoje)
    try:
        from historico import carregar_periodo, salvar, comparar
        historico = carregar_periodo(365, hoje)
        print(f"Histórico carregado: {len(historico)} dias\n")
    except Exception as e:
        print(f"Aviso histórico: {e}")
        historico = []

    # 5 — Sinais longitudinais
    try:
        from motor_padroes import detectar_sinais
        sinais = detectar_sinais(historico, dados)
        print(f"Sinais detectados: {sinais.get('n_sinais')} (mudança relevante: {sinais.get('houve_mudanca_relevante')})\n")
    except Exception as e:
        print(f"Aviso sinais: {e}")
        sinais = {"sinais": [], "n_sinais": 0, "houve_mudanca_relevante": False}

    # 6 — Modelo carga-resposta individual
    try:
        ontem = (hoje - timedelta(days=1)).isoformat()
        reg_ontem = next((r for r in historico if r.get("data") == ontem), None)
        peso_ontem = (reg_ontem or {}).get("_carga", {}).get("peso_carga_dia", 0) if reg_ontem else 0
        modelo_cr = modelo_carga_resposta(historico, dados, peso_ontem)
        print(f"Modelo carga-resposta: {modelo_cr.get('status')} (confiança {modelo_cr.get('confianca')})\n")
    except Exception as e:
        print(f"Aviso modelo CR: {e}")
        modelo_cr = {"status": "indisponivel", "confianca": "baixa"}

    # 7 — Salvar histórico de hoje (com campos dos motores)
    try:
        dados["treino"] = treino
        salvar(dados)
        comparacoes = comparar(dados)
    except Exception as e:
        print(f"Aviso salvar: {e}")
        comparacoes = {}

    # 8 — Interpretação (fisiologista)
    try:
        from gerar_briefing import gerar_briefing, enviar_email
        print("Interpretando (fisiologista)...")
        briefing = gerar_briefing(dados, comparacoes, treino, sinais, carga, modelo_cr)
        print("\n" + "="*50)
        print(briefing)
        print("="*50 + "\n")
    except Exception as e:
        print(f"Erro no briefing: {e}"); traceback.print_exc(); sys.exit(1)

    # 9 — Email
    try:
        modo = "[!] " if sinais.get("houve_mudanca_relevante") else ""
        assunto = f"{modo}Fisiologista — {hoje.strftime('%d/%m/%Y')}"
        print("Enviando email...")
        enviar_email(assunto, briefing)
        print("Concluído!")
    except Exception as e:
        print(f"Erro no email: {e}"); traceback.print_exc(); sys.exit(1)


if __name__ == "__main__":
    main()
