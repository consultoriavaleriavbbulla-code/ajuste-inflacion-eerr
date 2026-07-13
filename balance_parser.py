"""
Parser del balance provisional exportado del sistema contable.

Detecta dinamicamente las columnas "Saldo" (Total y una por cada mes del
ejercicio, en el orden en que vienen en el archivo) y descarta filas que no
sean cuentas reales (separadores, fila "Total" general, etc.).
"""
import re
import pandas as pd

CODIGO_PATTERN = re.compile(r"^\d+(\.\d+){2,}$")


def load_balance(file) -> dict:
    """
    file: ruta o file-like del Excel exportado del sistema.

    Devuelve:
        {
            "df": DataFrame con columnas ['codigo', 'nombre', 'total', <mes1>, <mes2>, ...],
            "meses": lista de nombres de mes en el orden del ejercicio (segun el archivo)
        }
    """
    raw = pd.read_excel(file, sheet_name=0, header=0)
    cols = list(raw.columns)

    if len(cols) < 3:
        raise ValueError("El archivo no tiene el formato esperado (faltan columnas).")

    codigo_col = cols[0]
    nombre_col = cols[1]

    saldo_cols = [c for c in cols if isinstance(c, str) and c.strip().endswith("- Saldo")]
    if not saldo_cols:
        raise ValueError("No se encontraron columnas 'Saldo' en el archivo.")

    total_col = None
    mes_cols = []
    for c in saldo_cols:
        label = c.split(" - ")[0].strip()
        if label.lower() == "total":
            total_col = c
        else:
            mes_cols.append(c)

    if total_col is None:
        raise ValueError("No se encontro la columna 'Total - Saldo'.")

    meses = [c.split(" - ")[0].strip() for c in mes_cols]

    out = raw[[codigo_col, nombre_col, total_col] + mes_cols].copy()
    out.columns = ["codigo", "nombre"] + ["total"] + meses

    # Solo filas cuyo codigo tiene forma de cuenta contable (ej. 4.1.010.10.001)
    out["codigo"] = out["codigo"].astype(str).str.strip()
    out = out[out["codigo"].str.match(CODIGO_PATTERN)]

    out["nombre"] = out["nombre"].fillna("").astype(str).str.strip()

    for c in ["total"] + meses:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    out = out.reset_index(drop=True)

    if out.empty:
        raise ValueError("No se detectaron cuentas validas en el archivo.")

    return {"df": out, "meses": meses}
