import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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

 

    full_path_socios = gf.construir_path(
        config["Insumos"]["path_insumos"], 
        config["Insumos"]["base_socios"]["nom_base"]
    )

    df_Bas_Socio = gf.leer_excel_columnas(
        ruta=full_path_socios,
        sheet_name=config["Insumos"]['base_socios']['sheet'],  
        columnas=None,
        dtype=str,
    )

    
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
    col_client_directa_completa_Socios = dict_cols['df_u_directa_completa_Socios']['id_cliente']
    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset=col_client_directa_completa_Socios, keep="first"
    )  # No es necesaria

    # Aplicamos reglas de negocio
    df_u_directa_completa_Socios = Aplicar_Regla_Negocio_Z1_ZA(
        df_u_directa_completa_Socios
    )

    df_u_directa_completa_Socios = Aplicar_regla_Negocio_Socio(
        df_u_directa_completa_Socios
    )

    col_socio = dict_cols["df_socios"]["col_socio"]

    df_si_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios[col_socio] == "SI"  # Preguntar
    ].copy()
    df_no_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios[col_socio] == "NO"
    ].copy()

    id_cliente = dict_cols["df_socios"]["id_cliente"]

    df_no_socios = df_no_socios.drop_duplicates(subset=id_cliente, keep="first")

    df_u_directa_completa_Socios = pd.concat([df_si_socios, df_no_socios])          

   
    full_path_indirecta = gf.construir_path(
        config["Insumos"]["path_insumos"], 
        config["Insumos"]["universo_indirecta"]["nom_base"]
    )

    df_u_indirecta = gf.leer_excel_columnas(
        ruta=full_path_indirecta,
        sheet_name=config["Insumos"]["universo_indirecta"]["sheet"],
        columnas=None,
        dtype=str,
    )

  
    full_path_dr_coord = gf.construir_path(
        config["Insumos"]["path_insumos"], 
        config["Insumos"]["drv_coordenadas"]["nom_base"]
    )

    df_coord = gf.leer_excel_columnas(
        ruta=full_path_dr_coord,
        sheet_name=config["Insumos"]["drv_coordenadas"]["sheet"],
        columnas=None,
        dtype=str,
    )

    cols_df_coord_dir = dict_cols["drv_coordenadas"]["directa"]
    agent_com_df_coord = dict_cols["drv_coordenadas"]["cod_agen_comer"]
    cols_dir = list(cols_df_coord_dir.values())  
    df_coord_dir = df_coord[df_coord["Agente Comercial"].isnull()][cols_dir]

    cols_coord_ind = dict_cols["drv_coordenadas"]["indirecta"]
    cols_ind = list(cols_coord_ind.values())    
    df_coord_ind = df_coord[~df_coord[agent_com_df_coord].isnull()][cols_ind]

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset=col_client_directa_completa_Socios, keep="first"
    )

    id_cliente_coord_dir = dict_cols["drv_coordenadas"]['directa']["id_cliente"]

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.merge(
        df_coord_dir, left_on=col_client_directa_completa_Socios, right_on=id_cliente_coord_dir, how="left"
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

    Llav_comp_col = dict_cols["drv_coordenadas"]["llave_compuesta"]
    col_lat = dict_cols["drv_coordenadas"]["indirecta"]["Grado_latitud"]
    col_long = dict_cols["drv_coordenadas"]["indirecta"]["Grado_longitud"]
    df_u_indirecta = df_u_indirecta.merge(
        df_coord_ind[[Llav_comp_col, col_lat, col_long]],
        on=Llav_comp_col,
        how="left",
    )

    df_u_indirecta = df_u_indirecta.drop(Llav_comp_col, axis=1)



    #####################################
    # lectura y concatenación de Insumos/directa
    ######################################


    full_path_dir_directa = gf.construir_path(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["Path_Directa"]["path"],
    )

    patron = config["Insumos"]["Path_Directa"]["patron"]

    dfs_ventas_directa = gf.leer_excels_dir(
        full_path_dir_directa, patron=patron, dtype=str
    )  # Lista


    dfs_procesadas_dir = [tf.cambiar_ventas_por_marca(df.copy()) for df in dfs_ventas_directa]   #Preguntarle a Daniel 
    df_ventas_directa = tf.concatenar_vertical(dfs_procesadas_dir)  
    

    ######################################
    # lectura y concatencioón de Insumos/indirecta
    ######################################

    full_path_dir_indirecta = os.path.join(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["Path_Indirecta"]["path"],
    )
    dfs_ventas_indirecta = gf.leer_excels_dir(full_path_dir_indirecta, patron=patron, dtype=str)
    dfs_formateados_ind = [tf.cambiar_form_vts_ind_dataframe(df.copy()) for df in dfs_ventas_indirecta]    

    dfs_procesadas_ind= [tf.cambiar_ventas_por_marca(df.copy()) for df in dfs_formateados_ind]
    dfs_ventas_indirecta = tf.concatenar_vertical(dfs_procesadas_ind)


    ###Resultado Directda 
    id_clie_vtas_dirc = dict_cols["df_ventas_directa"]["id_cliente"]

    df_u_directa_resultado = pd.merge(
    df_u_directa_completa_Socios, 
    df_ventas_directa, 
    left_on= id_cliente_coord_dir,
    right_on= id_clie_vtas_dirc, 
    how='left'
    )


    ###Resultado indirecta 

     
    
    col_id_agente_ind = dict_cols["universo_indirecta"]["cod_agente"]
    col_id_cliente_ind = dict_cols["universo_indirecta"]["id_cliente"]


    col_id_agente_vts_ind = dict_cols["df_ventas_indirecta"]["cod_agente"]
    col_ECOM_vts_ind = dict_cols["df_ventas_indirecta"]["cod_ECOM"]

    df_u_indirecta_resultado = pd.merge(
    df_u_indirecta, 
    dfs_ventas_indirecta, 
    left_on=[col_id_agente_ind, col_id_cliente_ind],
    right_on=[col_id_agente_vts_ind, col_ECOM_vts_ind],
    how='left'
    ) 

    
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
  

    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["directa_vts_csv"], df=df_u_directa_resultado
    )

    gf.exportar_a_excel(
        ruta_archivo=config["outputs"]["indirecta_vts_csv"], df=df_u_indirecta_resultado
    )


if __name__ == "__main__":

    main()
