"""
Persistencia simple (archivos JSON) de la configuracion de cada cliente:
  - que cuentas ajustan por inflacion y cuales no (por codigo de cuenta)

Un archivo por cliente en data/clientes/<cliente>.json, de forma que al
volver a subir un balance del mismo cliente (mes siguiente, o corregido) se
recupera automaticamente lo tildado la vez anterior.
"""
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "clientes")
os.makedirs(DATA_DIR, exist_ok=True)


def _slug(nombre: str) -> str:
    safe = "".join(c for c in nombre if c.isalnum() or c in (" ", "_", "-")).strip()
    return safe.replace(" ", "_") or "cliente"


def _path(cliente: str) -> str:
    return os.path.join(DATA_DIR, f"{_slug(cliente)}.json")


def listar_clientes() -> list:
    if not os.path.isdir(DATA_DIR):
        return []
    return sorted(f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json"))


def cargar_config(cliente: str) -> dict:
    """Devuelve dict {codigo_cuenta: bool} guardado para ese cliente."""
    path = _path(cliente)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("cuentas_ajustables", {})
    return {}


def guardar_config(cliente: str, cuentas_ajustables: dict) -> None:
    path = _path(cliente)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"cuentas_ajustables": cuentas_ajustables}, f, ensure_ascii=False, indent=2)
