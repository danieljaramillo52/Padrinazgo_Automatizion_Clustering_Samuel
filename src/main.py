import sys
import os
from pathlib import Path
import pandas as pd
import config_path_routes
from Utils import general_functions as gf
from Utils import Aplicar_Regla_Negocio_Z1_ZA, Aplicar_regla_Negocio_Socio
from Utils import transformation_functions as tf
from loguru import logger
import importlib

importlib.reload(gf)


def main():
    config = gf.procesar_configuracion(
        nom_archivo_configuracion="Controllers/setting/config.yml"
    )

    # Dict columnas.
    dict_cols = config.get("dict_cols", {})

    # col_directa
    id_u_dir = dict_cols["universo_directa"]["id_cliente"]
    id_soc = dict_cols["base_socios"]["id_cliente"]

    # Separar columnas totales por archivo
    cols_univ_dir = dict_cols["universo_directa"]
    cols_socios = dict_cols["base_socios"]
    # cols_univ_indir = dict_cols["Universo_Indirecta"]

    # Sleccionar columna única.
    cols_univ_dir["funcion_inter"]
    cols_univ_dir["sociedad"]  # estos son ejemplos, no cambiar
    cols_socios["id_cliente"]

    logger.info("Validando archivos")

    # Directorio insumos
    dir_insumos = Path(config["Insumos"]["path_insumos"]).resolve()

    # Extraer rutas completas.
    path_insumos = {
        f: os.path.join(dir_insumos, f)
        for f in os.listdir(dir_insumos)
        if f.lower().endswith((".xlsx", "xlsm"))
    }

    gf.validar_archivos(archivos=path_insumos)

    full_path_directa = gf.construir_path(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["universo_directa"]["nom_base"],
    )

    df_u_directa = gf.leer_excel_columnas(
        ruta=full_path_directa,  # Importacion de indirecta
        sheet_name=config["Insumos"]["universo_directa"]["sheet"],
        columnas=list(cols_univ_dir.values()),
        dtype=str,
    )

    full_path_socios = os.path.join(
        config["Insumos"]["path_insumos"], config["Insumos"]["base_socios"]["nom_base"]
    )

    df_Bas_Socio = gf.leer_excel_columnas(
        ruta=full_path_socios,
        sheet_name="Consolidado",  # Importación de Base socios
        columnas=None,
        dtype=str,
    )

    # eliminar duplicados
    df_u_directa = df_u_directa.drop_duplicates(subset=id_u_dir, keep="first")
    df_Bas_Socio = df_Bas_Socio.drop_duplicates(subset=id_soc, keep="first")

    path_columnas_socios_merge = list(
        config["Insumos"]["base_socios"]["columnas_socios_merge"].values()
    )

    df_u_directa_completa_Socios = df_u_directa.merge(
        df_Bas_Socio[[id_soc] + path_columnas_socios_merge],
        left_on=id_u_dir,
        right_on=id_soc,  # Merge de Directa con socios
        how="left",
    )

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset="Cód. Cliente", keep="first"
    )  # No es necesaria

    # Aplicamos reglas de negocio
    df_u_directa_completa_Socios = Aplicar_Regla_Negocio_Z1_ZA(
        df_u_directa_completa_Socios
    )

    df_u_directa_completa_Socios = Aplicar_regla_Negocio_Socio(
        df_u_directa_completa_Socios
    )

    df_si_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios["Col_Socio"] == "SI"  # Preguntar
    ].copy()
    df_no_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios["Col_Socio"] == "NO"
    ].copy()

    df_no_socios = df_no_socios.drop_duplicates(subset="Cód. Cliente", keep="first")

    df_u_directa_completa_Socios = pd.concat([df_si_socios, df_no_socios])             #Error

    # Leemos Universo indirecto
    full_path_indirecta = os.path.join(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["universo_indirecta"]["nom_base"],
    )

    df_u_indirecta = gf.leer_excel_columnas(
        ruta=full_path_indirecta,
        sheet_name=config["Insumos"]["universo_indirecta"]["sheet"],
        columnas=None,
        dtype=str,
    )

    # leemos drv de coordendas
    full_path_dr_coord = os.path.join(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["drv_coordenadas"]["nom_base"],
    )

    df_coord = gf.leer_excel_columnas(
        ruta=full_path_dr_coord,
        sheet_name="Base",
        columnas=None,
        dtype=str,
    )

    df_coord_dir = df_coord[df_coord["Agente Comercial"].isnull()][
        ["Cliente", "Grado latitud", "Grad.long."]
    ]
    df_coord_ind = df_coord[~df_coord["Agente Comercial"].isnull()][
        ["Agente Comercial", "Código ECOM", "Grado latitud", "Grad.long."]
    ]

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset="Cód. Cliente", keep="first"
    )

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.merge(
        df_coord_dir, left_on="Cód. Cliente", right_on="Cliente", how="left"
    )

    cfg_concat_drv = config["Insumos"]["drv_coordenadas"]["concatenar_cols"]

    cfg_concat_un_indir = config["Insumos"]["universo_indirecta"]["concatenar_cols"]

    df_coord_ind = tf.concatenar_columnas_pd(
        df=df_coord_ind,
        cols_elegidas=cfg_concat_drv["cols"],
        nueva_columna=cfg_concat_drv["nueva_columna"],
        usar_separador=cfg_concat_drv["usar_separador"],
        separador=cfg_concat_drv["separador"],
    )

    df_u_indirecta = tf.concatenar_columnas_pd(
        df=df_u_indirecta,
        cols_elegidas=cfg_concat_un_indir["cols"],
        nueva_columna=cfg_concat_un_indir["nueva_columna"],
        usar_separador=cfg_concat_un_indir["usar_separador"],
        separador=cfg_concat_un_indir["separador"],
    )

    df_u_indirecta = df_u_indirecta.merge(
        df_coord_ind[["llave_compuesta", "Grado latitud", "Grad.long."]],
        on="llave_compuesta",
        how="left",
    )

    df_u_indirecta = df_u_indirecta.drop("llave_compuesta", axis=1)

    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["directa_xlsx"], df=df_u_directa_completa_Socios
    )

    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["directa_csv"], df=df_u_directa_completa_Socios
    )

    # INDIRECTA
    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["indirecta_xlsx"], df=df_u_indirecta
    )

    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["indirecta_csv"], df=df_u_indirecta
    )

    #####################################
    # lectura y concatenación de Insumos/directa
    ######################################

    full_path_dir_directa = os.path.join(
        config["Insumos"]["path_insumos"], config["Insumos"]["Path_Directa"]["path"]
    )

    patron = config["Insumos"]["Path_Directa"]["patron"]

    dfs_ventas_directa = gf.leer_excels_dir(
        full_path_dir_directa, patron=patron, dtype=str
    )  # Lista

    df_ventas_directa = tf.concatenar_vertical(dfs_ventas_directa)  # Dataframe

    ######################################
    # lectura y concatencioón de Insumos/indirecta
    ######################################

    full_path_dir_indirecta = os.path.join(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["Path_Indirecta"]["path"],
    )

    sheet_name = config["Insumos"]["Path_Indirecta"]["sheet"]

    dfs_ventas_indirecta = gf.leer_excels_dir(full_path_dir_indirecta, patron=patron)

    df_vts_ind = pd.read_excel("Insumos/Indirecta/BDVentasIndirecta_2022.12_11.xlsx")

    df_coord_ind = df_vts_ind.copy()

    df_vts_ind = df_vts_ind.rename(
        columns={
            "Unnamed: 0": "Agente Comercial",
            "Unnamed: 1": "Código ECOM",
            "Unnamed: 2": "Marca",
        },
    )

    # df_vts_ind = df_vts_ind[
    #    (df_vts_ind["Agente Comercial"].notna())
    #    & (df_vts_ind["Agente Comercial"] != "Agente Comercial")
    # ].reset_index(drop=True)

    columnas_cop = {}
    columnas_kg = {}

    COLS_NO_VTAS = ["Agente Comercial", "Código ECOM", "Marca"]

    for col in df_vts_ind.columns:
        if col not in COLS_NO_VTAS:
            tipo = df_vts_ind[col].iloc[1]
            mes = df_vts_ind[col].iloc[0]

            if tipo == "COP":
                columnas_cop[col] = mes
            elif tipo == "KG":
                columnas_kg[col] = mes

    df_vts_ind = df_vts_ind.iloc[2:].reset_index(drop=True)

    df_vtas_cop = df_vts_ind[COLS_NO_VTAS + list(columnas_cop.keys())]
    df_vtas_cop.rename(columns=columnas_cop, inplace=True)

    meses_cop = list(columnas_cop.values())
    df_cop = df_vtas_cop[COLS_NO_VTAS + meses_cop].melt(
        id_vars=COLS_NO_VTAS,
        var_name="Mes",
        value_name="Venta $",
    )

    df_vtas_kg = df_vts_ind[COLS_NO_VTAS + list(columnas_kg.keys())]
    df_vtas_kg.rename(columns=columnas_kg, inplace=True)

    meses_kg = list(columnas_kg.values())
    df_kg = df_vtas_kg[COLS_NO_VTAS + meses_kg].melt(
        id_vars=COLS_NO_VTAS,
        var_name="Mes",
        value_name="Venta Kg",
    )

    df_final = pd.merge(df_cop, df_kg, on=COLS_NO_VTAS + ["Mes"], how="outer")
    df_final = df_final[
        ["Agente Comercial", "Código ECOM", "Mes", "Marca", "Venta $", "Venta Kg"]
    ]

    df_final.to_excel("Resultados/df_final2.xlsx", index=False)

    df_final = tf.cambiar_ventas_por_marca(df_final)


if __name__ == "__main__":

    main()
