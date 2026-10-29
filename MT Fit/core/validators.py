"""Validações simples compartilhadas pelas rotas."""
import re
from datetime import datetime


def limpar_texto(valor):
    return (valor or "").strip()


def validar_email(email):
    return bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", limpar_texto(email)))


def validar_cpf(cpf):
    n = ''.join(ch for ch in (cpf or '') if ch.isdigit())
    if len(n) != 11 or n == n[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(n[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11
        if digito == 10:
            digito = 0
        if digito != int(n[tamanho]):
            return False
    return True


def validar_data_hora(data, horario):
    try:
        datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M")
        return True
    except (ValueError, TypeError):
        return False
