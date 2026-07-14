"""
Lee un Excel con los indices FACPCE (dos columnas: Mes e Indice) y los
matchea contra los meses detectados en el balance, sin importar mayusculas,
acentos o espacios.
"""
import unicodedata
import pandas as pd


def _normalizar(texto) -> str:
    s = str(texto).strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return s


def load_indices(file, meses: list):
    """
    file: Excel subido (dos columnas: nombre de mes y valor de indice).
    meses: lista de meses detectados en el balance (para matchear).

    Devuelve (indices_encontrados, meses_no_reconocidos):
        indices_encontrados: dict {mes: valor_float}
        meses_no_reconocidos: lista de textos de la primera columna que no
            se pudieron matchear contra ningun mes del ejercicio.
    """
    raw = pd.read_excel(file, sheet_name=0, header=0)

    if raw.shape[1] < 2:
        raise ValueError("El archivo debe tener al menos dos columnas: Mes e Indice.")

    col_mes, col_indice = raw.columns[0], raw.columns[1]
    sub = raw[[col_mes, col_indice]].dropna(how="all")

    lookup = {_normalizar(m): m for m in meses}

    encontrados = {}
    no_reconocidos = []

    for _, fila in sub.iterrows():
        mes_raw = fila[col_mes]
        val_raw = fila[col_indice]
        if pd.isna(mes_raw) or pd.isna(val_raw):
            continue
        clave = _normalizar(mes_raw)
        if clave in lookup:
            try:
                encontrados[lookup[clave]] = float(val_raw)
            except (TypeError, ValueError):
                no_reconocidos.append(str(mes_raw))
        else:
            no_reconocidos.append(str(mes_raw))

    if not encontrados:
        raise ValueError(
            "No se reconocio ningun mes. La primera columna debe tener los nombres "
            "de mes (Julio, Agosto, etc.) y la segunda el valor del indice."
        )

    return encontrados, no_reconocidos
