"""
ATLETAS — busca todos os atletas ativos no Supabase
e descriptografa as credenciais Garmin para o pipeline.
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def _descriptografar(senha_encriptada: str, encryption_key: str) -> str:
    """
    Descriptografa a senha AES-GCM salva pelo formulário JavaScript.
    O JS usa crypto.subtle com AES-GCM 128-bit IV (12 bytes) e tag de 128 bits.
    Formato salvo: base64(iv) + '.' + base64(ciphertext+tag)
    """
    partes = senha_encriptada.split('.')
    if len(partes) != 2:
        raise ValueError("Formato de senha inválido")

    iv = base64.b64decode(partes[0])
    ciphertext_with_tag = base64.b64decode(partes[1])

    # Chave: 32 bytes (padded ou truncado)
    key = encryption_key.ljust(32, '0')[:32].encode()

    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(iv, ciphertext_with_tag, None)
    return decrypted.decode('utf-8')


def buscar_atletas() -> list[dict]:
    """
    Busca todos os atletas ativos no Supabase.
    Retorna lista com nome, email, garmin_email e garmin_password descriptografado.
    """
    import urllib.request
    import json

    url = os.getenv("SUPABASE_URL") + "/rest/v1/atletas?ativo=eq.true&select=*"
    service_key = os.getenv("SUPABASE_SERVICE_KEY")
    encryption_key = os.getenv("ENCRYPTION_KEY")

    req = urllib.request.Request(url, headers={
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
    })

    with urllib.request.urlopen(req) as res:
        atletas = json.loads(res.read())

    resultado = []
    for a in atletas:
        try:
            senha = _descriptografar(a["garmin_password"], encryption_key)
            resultado.append({
                "id": a["id"],
                "nome": a["nome"],
                "email": a["email"],
                "garmin_email": a["garmin_email"],
                "garmin_password": senha,
            })
        except Exception as e:
            print(f"Erro ao descriptografar senha de {a.get('email')}: {type(e).__name__}: {e}")

    return resultado


def atualizar_ultimo_briefing(atleta_id: str):
    """Atualiza o campo ultimo_briefing para agora."""
    import urllib.request
    import json
    from datetime import datetime, timezone

    url = os.getenv("SUPABASE_URL") + f"/rest/v1/atletas?id=eq.{atleta_id}"
    service_key = os.getenv("SUPABASE_SERVICE_KEY")

    data = json.dumps({"ultimo_briefing": datetime.now(timezone.utc).isoformat()}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH", headers={
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    })
    try:
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Aviso: não atualizou ultimo_briefing: {e}")
