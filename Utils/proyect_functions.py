import os
import pandas as pd
from Utils.general_functions import logger, cargar_multiples_archivos
from Utils.transformation_functions import agregar_ventas_por_cliente_y_marca, merge_ventas_con_universo


def complementar_directa(universo_df: pd.DataFrame, socios_df: pd.DataFrame, dict_cols: dict) -> pd.DataFrame:
    """
    Complementa la información del universo de clientes directos con la base de socios.
    """
    id_cliente_uni = dict_cols["universo_directa"]["id_cliente"]
    id_cliente_soc = dict_cols["base_socios"]["id_cliente"]
    vendedor_col = dict_cols["universo_directa"]["funcion_inter"]

    df = universo_df.merge(
        socios_df,
        how="left",
        left_on=id_cliente_uni,
        right_on=id_cliente_soc,
    )

    df[vendedor_col] = df[vendedor_col].where(df[vendedor_col].isin(["Z1", "ZA"]), "Sin asignar")
    df["Socio"] = df[id_cliente_uni].isin(socios_df[id_cliente_soc]).map({True: "SI", False: "NO"})

    prioridad = {"Z1": 0, "ZA": 1, "Sin asignar": 2}
    df = df.sort_values(by=[id_cliente_uni, vendedor_col], key=lambda col: col.map(prioridad))
    df = df.drop_duplicates(subset=[id_cliente_uni], keep="first")

    df = df.drop(columns=["Cod_Agente", "Nom_Agente"], errors="ignore")

    logger.info("Universo Directa complementado y procesado")
    return df


def procesar_ventas_directa(ventas_dir: str) -> pd.DataFrame:
    """
    Carga y concatena todas las bases de ventas directa desde un directorio.

    Args:
        ventas_dir (str): Ruta del directorio con los archivos de ventas.

    Returns:
        pd.DataFrame: DataFrame unificado con todas las ventas.
    """
    if not os.path.exists(ventas_dir):
        logger.warning(f"No existe el directorio de ventas: {ventas_dir}")
        return pd.DataFrame()

    ventas_files = [
        os.path.join(ventas_dir, f)
        for f in os.listdir(ventas_dir)
        if "venta" in f.lower() and f.lower().endswith((".xlsx", ".xls", ".csv", ".parquet"))
    ]

    if not ventas_files:
        logger.warning(f"No se encontraron archivos de ventas en: {ventas_dir}")
        return pd.DataFrame()

    logger.info(f"Se encontraron {len(ventas_files)} archivos de ventas para procesar.")
    return cargar_multiples_archivos(ventas_files)


def integrar_ventas_con_universo(
    universo_df: pd.DataFrame,
    ventas_df: pd.DataFrame,
    dict_cols: dict,
    editable_cfg: dict,
) -> pd.DataFrame:
    """
    Integra el universo directa con las ventas agregadas por periodo.

    Args:
        universo_df (pd.DataFrame): Universo directa.
        ventas_df (pd.DataFrame): Ventas concatenadas.
        dict_cols (dict): Diccionario de columnas.
        editable_cfg (dict): Periodo editable.yml (start_year, end_year, etc.).

    Returns:
        pd.DataFrame: Universo con columnas agregadas de ventas.
    """
    if ventas_df.empty:
        logger.warning("DataFrame de ventas vacío, no se integrará con el universo.")
        return universo_df

    ventas_agg = agregar_ventas_por_cliente_y_marca(
        ventas_df,
        cliente_col="Cliente",
        marca_col="Marca",
        pesos_col="Venta $",
        kg_col="Venta Kg",
        start_year=editable_cfg.get("start_year"),
        end_year=editable_cfg.get("end_year"),
        start_month=editable_cfg.get("start_month"),
        end_month=editable_cfg.get("end_month"),
    )

    universo_cliente_col = dict_cols["universo_directa"]["id_cliente"]

    logger.info(f"Columnas en ventas_agg: {ventas_agg.columns.tolist()}")
    return merge_ventas_con_universo(universo_df, ventas_agg, universo_cliente_col, "cliente", how="left")

