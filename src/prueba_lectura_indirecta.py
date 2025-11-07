import pandas as pd
import re
from typing import Iterable, List, Tuple

df_vtas_indir = pd.read_excel(
    "Insumos/Indirecta/BDVentasIndirecta_2022.12_13.xlsx", dtype=str
)

df_vtas_indir = df_vtas_indir.rename(
    columns={
        "Unnamed: 0": "Agente Comercial",
        "Unnamed: 1": "Código ECOM",
        "Unnamed: 2": "Marca",
    },
    inplace=False,
)


def pares_vnaa(
    cols: Iterable[str], token_a: str = "$", token_b: str = "KG"
) -> List[Tuple[str, str]]:
    """
    Devuelve [(col_$, col_KG), ...] para columnas que contienen
    'Venta Neta Acum Año Actual', emparejadas por el mismo sufijo .n (sin sufijo = 0).
    """
    # 1) filtra solo las columnas del patrón fijo
    vcols = [c for c in cols if "Venta Neta Acum Año Actual" in c]

    def idx(name: str) -> int:
        m = re.search(r"\.(\d+)$", name)
        return int(m.group(1)) if m else 0  # sin sufijo -> 0

    A, B = {}, {}
    for c in vcols:
        # exige el token al final, con o sin .n (evita falsos positivos)
        if c.endswith(f" {token_a}") or re.search(rf" {re.escape(token_a)}\.\d+$", c):
            A[idx(c)] = c
        elif c.endswith(f" {token_b}") or re.search(rf" {re.escape(token_b)}\.\d+$", c):
            B[idx(c)] = c

    # intersección por índice y salida ordenada por índice
    comunes = sorted(set(A) & set(B))
    return [(A[i], B[i]) for i in comunes]


list_tuples_pares = pares_vnaa(df_vtas_indir.columns)

dfs_resultado = []  # por si luego quieres concatenar

for col_dol, col_kg in list_tuples_pares:
    cols_completas = ["Agente Comercial", "Código ECOM", "Marca", col_dol, col_kg]

    # Mes en la primera fila de la col_dol
    mes = df_vtas_indir[col_dol].iloc[0]

    # Slice de columnas
    df_vtas_indir_fil = df_vtas_indir[cols_completas].copy()

    # Renombrar SOLO el par actual
    df_vtas_indir_fil = df_vtas_indir_fil.rename(
        columns={
            col_dol: "venta $",
            col_kg: "venta KG",
        }
    )

    # Eliminar filas 0 y 1
    df_vtas_indir_fil = df_vtas_indir_fil.iloc[2:].reset_index(drop=True)

    # Añadir Año mes
    df_vtas_indir_fil["Año mes"] = mes

    dfs_resultado.append(df_vtas_indir_fil)

dfs_resultado
