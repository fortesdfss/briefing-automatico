"""
SCRIPT PRINCIPAL — Orquestrador multiusuário
Busca todos os atletas no Supabase e roda o pipeline para cada um.
"""

import sys
import traceback
from datetime import date, timedelta


def rodar_para_atleta(atleta: dict, hoje: date):
    """Roda o pipeline completo para um atleta."""
    nome = atleta["nome"]
    print(f"\n{'='*50}")
    print(f"  {nome.upper()} — {hoje.strftime('%d/%m/%Y')}")
    print(f"{'='*50}\n")

    # Injeta credenciais do atleta nas variáveis de ambiente temporariamente
    import os
    os.environ["GARMIN_EMAIL"] = atleta["garmin_email"]
    os.environ["GARMIN_PASSWORD"] = atleta["garmin_password"]
    os.environ["EMAIL_DESTINATARIO"] = atleta["email"]

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
        print(f"Erro na coleta: {e}")
        traceback.print_exc()
        return False

    # 2 — Treino segmentado
    try:
        from treino_prescrito_executado import coletar_treino
        print("Analisando treinos...")
        treino = coletar_treino(client, hoje)
        print(f"Modalidades: {treino.get('modalidades_do_dia')}\n")
    except Exception as e:
        print(f"Aviso treino: {e}")
        treino = {"prescrito": None, "atividades": [], "modalidades_do_dia": []}

    # 3 — Intenção e carga
    try:
        from motor_intencao_resposta import carga_do_dia, modelo_carga_resposta
        carga = carga_do_dia(dados, treino)
        dados["_carga"] = carga
    except Exception as e:
        print(f"Aviso intenção: {e}")
        carga = {"intencoes": [], "peso_carga_dia": 0}

    # 4 — Histórico
    try:
        from historico import carregar_periodo, salvar, comparar
        historico = carregar_periodo(365, hoje)
        print(f"Histórico: {len(historico)} dias\n")
    except Exception as e:
        print(f"Aviso histórico: {e}")
        historico = []

    # 5 — Sinais longitudinais
    try:
        from motor_padroes import detectar_sinais
        sinais = detectar_sinais(historico, dados)
    except Exception as e:
        print(f"Aviso sinais: {e}")
        sinais = {"sinais": [], "n_sinais": 0, "houve_mudanca_relevante": False}

    # 6 — Modelo carga-resposta
    try:
        ontem = (hoje - timedelta(days=1)).isoformat()
        reg_ontem = next((r for r in historico if r.get("data") == ontem), None)
        peso_ontem = (reg_ontem or {}).get("_carga", {}).get("peso_carga_dia", 0)
        modelo_cr = modelo_carga_resposta(historico, dados, peso_ontem)
    except Exception as e:
        print(f"Aviso modelo CR: {e}")
        modelo_cr = {"status": "indisponivel", "confianca": "baixa"}

    # 6b — Wellbeing
    try:
        from wellbeing import carregar_wellbeing
        bem_estar = carregar_wellbeing()
    except Exception as e:
        bem_estar = {"disponivel": False, "vencido": True}

    # 6c — Exclusão causal
    try:
        from motor_exclusao_causal import rodar_exclusao
        exclusoes = rodar_exclusao(treino, dados)
    except Exception as e:
        exclusoes = []

    # 6d — Não-resposta
    try:
        from motor_nao_resposta import detectar_nao_resposta
        nao_resposta = detectar_nao_resposta(historico)
    except Exception as e:
        nao_resposta = {"aplicavel": False}

    # 6e — Lacunas
    try:
        from motor_lacunas import identificar_lacunas
        lacunas = identificar_lacunas(exclusoes, dados, treino)
    except Exception as e:
        lacunas = []

    # 7 — Salvar histórico
    try:
        dados["treino"] = treino
        salvar(dados)
        comparacoes = comparar(dados)
    except Exception as e:
        print(f"Aviso salvar: {e}")
        comparacoes = {}

    # 8 — Gerar briefing
    try:
        from gerar_briefing import gerar_briefing, enviar_email
        print("Interpretando (fisiologista)...")
        briefing = gerar_briefing(dados, comparacoes, treino, sinais, carga,
                                  modelo_cr, bem_estar, exclusoes, nao_resposta, lacunas)
        print(f"Briefing gerado: modo {briefing.get('modo')}\n")
    except Exception as e:
        print(f"Erro no briefing: {e}")
        traceback.print_exc()
        return False

    # 9 — Enviar email
    try:
        from wellbeing import eh_domingo, formulario_html
        html_extra = formulario_html()  # TEST: sempre mostrar o formulário
        modo = "[!] " if sinais.get("houve_mudanca_relevante") or nao_resposta.get("relevante") else ""
        assunto = f"{modo}Briefing Fisiológico — {hoje.strftime('%d/%m/%Y')}"
        enviar_email(assunto, briefing, html_extra, bem_estar)
        print(f"Email enviado para {atleta['email']}")
    except Exception as e:
        print(f"Erro no email: {e}")
        traceback.print_exc()
        return False

    return True


def main():
    hoje = date.today()
    print(f"\nFISIOLOGISTA DIÁRIO — {hoje.strftime('%d/%m/%Y')}")
    print(f"Buscando atletas no Supabase...\n")

    # Busca atletas
    try:
        from atletas import buscar_atletas, atualizar_ultimo_briefing
        atletas = buscar_atletas()
        print(f"{len(atletas)} atleta(s) ativo(s)\n")
    except Exception as e:
        print(f"Erro ao buscar atletas: {e}")
        traceback.print_exc()
        sys.exit(1)

    if not atletas:
        print("Nenhum atleta ativo encontrado.")
        sys.exit(0)

    # Roda para cada atleta
    sucessos = 0
    for atleta in atletas:
        try:
            ok = rodar_para_atleta(atleta, hoje)
            if ok:
                atualizar_ultimo_briefing(atleta["id"])
                sucessos += 1
        except Exception as e:
            print(f"Erro inesperado para {atleta['nome']}: {e}")
            traceback.print_exc()

    print(f"\nConcluído: {sucessos}/{len(atletas)} atletas processados.")


if __name__ == "__main__":
    main()
