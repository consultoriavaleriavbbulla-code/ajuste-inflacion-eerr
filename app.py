"""
Herramienta de Ajuste por Inflacion del Estado de Resultados (RT 6 + RT 54 FACPCE)

Flujo:
 1. Elegir/crear cliente.
 2. Subir el balance provisional exportado del sistema contable (.xlsx).
 3. Completar el indice FACPCE de cada mes detectado en el archivo.
 4. Tildar que cuentas se ajustan por inflacion (se recuerda por cliente).
 5. Procesar y descargar el Estado de Resultados historico vs ajustado.
"""
import streamlit as st
import pandas as pd

from balance_parser import load_balance
from inflation_engine import calcular_ajuste
from excel_export import export_to_bytes
import storage

st.set_page_config(page_title="Ajuste por Inflacion - EERR", layout="wide")
st.title("Ajuste por Inflacion del Estado de Resultados")
st.caption("RT 6 + RT 54 FACPCE — VB Advisory")

# ---------------------------------------------------------------------------
# 1. Cliente
# ---------------------------------------------------------------------------
st.header("1. Cliente")
clientes_existentes = storage.listar_clientes()
col_a, col_b = st.columns([2, 1])
with col_a:
    opciones = ["-- Nuevo cliente --"] + clientes_existentes
    seleccion = st.selectbox("Cliente", opciones)
with col_b:
    if seleccion == "-- Nuevo cliente --":
        cliente = st.text_input("Nombre del nuevo cliente")
    else:
        cliente = seleccion
        st.text_input("Nombre del nuevo cliente", value="", disabled=True, placeholder="(usando cliente existente)")

if not cliente:
    st.info("Elegi o cargá un cliente para continuar.")
    st.stop()

# ---------------------------------------------------------------------------
# 2. Balance
# ---------------------------------------------------------------------------
st.header("2. Balance provisional")
archivo = st.file_uploader("Subi el Excel exportado del sistema contable", type=["xlsx"])

if not archivo:
    st.stop()

try:
    resultado = load_balance(archivo)
except ValueError as e:
    st.error(f"No se pudo leer el archivo: {e}")
    st.stop()

df = resultado["df"]
meses = resultado["meses"]
st.success(f"Se detectaron {len(df)} cuentas y {len(meses)} meses: {' -> '.join(meses)}")

# ---------------------------------------------------------------------------
# 3. Indices FACPCE por mes
# ---------------------------------------------------------------------------
st.header("3. Indices FACPCE (RT 6 + RT 54) de cada mes")
st.caption("El indice de cierre es el del ultimo mes del ejercicio (el mas a la derecha).")

if "indices_df" not in st.session_state or st.session_state.get("indices_meses") != meses:
    st.session_state["indices_df"] = pd.DataFrame({"Mes": meses, "Indice": [None] * len(meses)})
    st.session_state["indices_meses"] = meses

indices_editado = st.data_editor(
    st.session_state["indices_df"],
    column_config={
        "Mes": st.column_config.TextColumn(disabled=True),
        "Indice": st.column_config.NumberColumn(min_value=0.0, format="%.4f"),
    },
    hide_index=True,
    use_container_width=True,
    key="indices_editor",
)

indices = dict(zip(indices_editado["Mes"], indices_editado["Indice"]))
indices_completos = all(v not in (None, 0, "") for v in indices.values())
if not indices_completos:
    st.warning("Completa el indice de todos los meses para poder procesar.")

# ---------------------------------------------------------------------------
# 4. Cuentas ajustables
# ---------------------------------------------------------------------------
st.header("4. Cuentas que se ajustan por inflacion")
st.caption(
    "Por defecto se proponen ajustables todas las cuentas de resultado (regla general RT 6). "
    "Desmarca las que correspondan a partidas ya expresadas en moneda de cierre "
    "(resultados financieros, diferencias de cambio, RECPAM, etc.). "
    "La seleccion queda guardada para este cliente."
)

config_guardada = storage.cargar_config(cliente)

cuentas_df = df[["codigo", "nombre"]].copy()
cuentas_df["Ajusta por inflacion"] = cuentas_df["codigo"].map(
    lambda c: config_guardada.get(c, True)  # default: ajustable
)
cuentas_df = cuentas_df.rename(columns={"codigo": "Codigo", "nombre": "Cuenta"})

nuevas = [c for c in df["codigo"] if c not in config_guardada]
if nuevas and config_guardada:
    st.info(f"Hay {len(nuevas)} cuenta(s) nueva(s) respecto de la ultima vez (marcadas ajustables por defecto).")

cuentas_editado = st.data_editor(
    cuentas_df,
    column_config={
        "Codigo": st.column_config.TextColumn(disabled=True),
        "Cuenta": st.column_config.TextColumn(disabled=True),
        "Ajusta por inflacion": st.column_config.CheckboxColumn(),
    },
    hide_index=True,
    use_container_width=True,
    height=420,
    key="cuentas_editor",
)

cuentas_ajustables = dict(zip(cuentas_editado["Codigo"], cuentas_editado["Ajusta por inflacion"]))

# ---------------------------------------------------------------------------
# 5. Procesar
# ---------------------------------------------------------------------------
st.header("5. Procesar")

puede_procesar = indices_completos
if st.button("Calcular ajuste por inflacion", type="primary", disabled=not puede_procesar):
    storage.guardar_config(cliente, cuentas_ajustables)
    try:
        resultado_calc = calcular_ajuste(df, meses, indices, cuentas_ajustables)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.session_state["resultado_calc"] = resultado_calc
    st.session_state["indices_usados"] = dict(indices)
    st.session_state["cliente_usado"] = cliente
    st.session_state["meses_usados"] = meses

if "resultado_calc" in st.session_state:
    st.subheader("Vista previa")
    r = st.session_state["resultado_calc"]
    preview_cols = ["codigo", "nombre", "total", "total_ajustado"]
    preview = r[preview_cols].rename(
        columns={"codigo": "Codigo", "nombre": "Cuenta", "total": "Total Historico", "total_ajustado": "Total Ajustado"}
    )
    st.dataframe(preview, use_container_width=True, height=350)

    total_hist = r["total"].sum()
    total_aj = r["total_ajustado"].sum()
    c1, c2 = st.columns(2)
    c1.metric("Total historico del ejercicio", f"{total_hist:,.2f}")
    c2.metric("Total ajustado por inflacion", f"{total_aj:,.2f}")

    excel_bytes = export_to_bytes(
        st.session_state["resultado_calc"],
        st.session_state["meses_usados"],
        st.session_state["cliente_usado"],
        st.session_state["indices_usados"],
    )
    st.download_button(
        "Descargar Estado de Resultados ajustado (Excel)",
        data=excel_bytes,
        file_name=f"EERR_ajustado_{cliente.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
