"""
Motor de calculo del ajuste por inflacion (RT 6 + RT 54 FACPCE).

Formula por cuenta ajustable y por mes:
    Saldo ajustado(mes) = Saldo historico(mes) x (Indice de cierre / Indice del mes de origen)

El "Indice de cierre" es el indice del ultimo mes del ejercicio cargado
(el mes mas reciente presente en el archivo).

Las cuentas no marcadas como ajustables mantienen su valor historico.
"""
import pandas as pd


def calcular_ajuste(df: pd.DataFrame, meses: list, indices: dict, cuentas_ajustables: dict) -> pd.DataFrame:
    """
    df: DataFrame con columnas ['codigo', 'nombre', 'total', <mes1>, <mes2>, ...]
    meses: lista de meses en orden cronologico (tal como aparecen en el archivo)
    indices: dict {mes: valor_indice} - debe tener un valor para cada mes en `meses`
    cuentas_ajustables: dict {codigo: bool} - True = la cuenta se ajusta por inflacion

    Devuelve una copia de df con columnas adicionales:
        "<mes>_ajustado" por cada mes, y "total_ajustado"
    """
    faltantes = [m for m in meses if m not in indices or indices[m] in (None, 0, "")]
    if faltantes:
        raise ValueError(f"Faltan indices para los meses: {', '.join(faltantes)}")

    mes_cierre = meses[-1]
    indice_cierre = float(indices[mes_cierre])

    result = df.copy()
    ajusta_mask = result["codigo"].map(lambda c: bool(cuentas_ajustables.get(c, False)))

    for mes in meses:
        idx_mes = float(indices[mes])
        coef = indice_cierre / idx_mes if idx_mes else 1.0
        col_aj = f"{mes}_ajustado"
        result[col_aj] = result[mes]
        result.loc[ajusta_mask, col_aj] = result.loc[ajusta_mask, mes] * coef

    ajustada_cols = [f"{m}_ajustado" for m in meses]
    result["total_ajustado"] = result[ajustada_cols].sum(axis=1)

    return result
