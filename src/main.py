import sys
import os
import pandas as pd
import config_path_routes 
from Utils import general_functions as gf
from Utils import Aplicar_Regla_Negocio_Z1_ZA, Aplicar_regla_Negocio_Socio
from Utils import transformation_functions as tf
from loguru import logger




def main():
    config = gf.procesar_configuracion(
        nom_archivo_configuracion="Controllers/setting/config.yml"
    )

    # Dict columnas.
    dict_cols = config.get("dict_cols", {})

    #col_directa
    id_u_dir = dict_cols['universo_directa']['id_cliente']
    id_soc = dict_cols['base_socios']['id_cliente']

    # Separar columnas totales por archivo
    cols_univ_dir = dict_cols["universo_directa"]
    cols_socios = dict_cols["base_socios"]
    #cols_univ_indir = dict_cols["Universo_Indirecta"]

    # Sleccionar columna única.
    cols_univ_dir["funcion_inter"]
    cols_univ_dir["sociedad"]
    cols_socios["id_cliente"]
    
  
    logger.info("Validando archivos")

   
    gf.Validar_Archivos()
    print("\n--------------\n")

    print("Leyendo Universo Directa\n")
    # pd.read_excel(config['Insumos']['path_insumos'] + config['Insumos']['universo_directa']['nom_base'])

    full_path_directa = os.path.join(
        config["Insumos"]["path_insumos"],
        config["Insumos"]["universo_directa"]["nom_base"],
    )
 
    df_u_directa = gf.leer_excel_columnas(
        ruta=full_path_directa,    #Importacion de indirecta
        sheet_name="Maestra",
        columnas=list(cols_univ_dir.values()),  
        dtype=str,
        nombre_lectura="Universo Directa"
    )

    print(df_u_directa.head())

    print(df_u_directa.columns)
   

    print("Leyendo Base Socios\n")
    full_path_socios = os.path.join(
        config["Insumos"]["path_insumos"], config["Insumos"]["base_socios"]["nom_base"]
    )

    df_Bas_Socio = gf.leer_excel_columnas(
        ruta=full_path_socios,       
        sheet_name="Consolidado",    #Importación de Base socios 
        columnas= None,  
        dtype=str,
        nombre_lectura="Base socios"
    )

    #eliminar duplicados
    df_u_directa = df_u_directa.drop_duplicates(subset=id_u_dir, keep="first")
    df_Bas_Socio = df_Bas_Socio.drop_duplicates(subset=id_soc, keep="first")

    columnas_socios = [
        "Atención",
        "Tipo Socios",
        "Cod_vend Z1",
        "Nom_Vend Z1",
        "Cod_vend ZA",
        "Nom_Vend ZA",
    ]
  

    df_u_directa_completa_Socios = df_u_directa.merge(
        df_Bas_Socio[[id_soc] + columnas_socios],
        left_on=id_u_dir,
        right_on=id_soc,  #Merge de Directa con socios
        how="left",
    )


    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset="Cód. Cliente", keep="first"
    )   #No es necesaria

    #Aplicamos reglas de negocio 
    df_u_directa_completa_Socios = Aplicar_Regla_Negocio_Z1_ZA(
        df_u_directa_completa_Socios
    )

    df_u_directa_completa_Socios = Aplicar_regla_Negocio_Socio(
        df_u_directa_completa_Socios
    )

    df_si_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios["Col_Socio"] == "SI"
    ].copy()
    df_no_socios = df_u_directa_completa_Socios[
        df_u_directa_completa_Socios["Col_Socio"] == "NO"
    ].copy()

    df_no_socios = df_no_socios.drop_duplicates(subset="Cód. Cliente", keep="first")

    df_u_directa_completa_Socios = pd.concat([df_si_socios, df_no_socios])

   
    #Leemos Universo indirecto
    full_path_indirecta = os.path.join(
        config["Insumos"]["path_insumos"], config["Insumos"]["universo_indirecta"]["nom_base"]
    )

    df_u_indirecta = gf.leer_excel_columnas(
        ruta = full_path_indirecta,
        sheet_name = 'BD',
        columnas = None,
        dtype= str,
        nombre_lectura = 'Universo Indirecta'
    )

    #leemos drv de coordendas
    full_path_dr_coord = os.path.join(
         config["Insumos"]["path_insumos"], config["Insumos"]["drv_coordenadas"]["nom_base"]
    )

    df_coord = gf.leer_excel_columnas(
        ruta=full_path_dr_coord,
        sheet_name='Base',
        columnas= None,
        dtype= str,
        nombre_lectura= 'Driver de Coordenada'
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

    # df_u_directa_completa_Socios = df_u_directa_completa_Socios.dropna(
    # subset=['Grado latitud', 'Grad.long.'],
    # how='all'  # Elimina si TODAS están vacías
    # )

    # df_u_directa_completa_Socios = df_u_directa_completa_Socios.dropna(
    # subset=['Grado latitud', 'Grad.long.'],
    # how='any'  # Elimina si ALGUNA está vacía
    # )

    # DIRECTA
    df_u_directa_completa_Socios.to_excel(
        r"Insumos\Universo_Directa_Resultado.xlsx",
        index=False,
    )

    df_u_directa_completa_Socios.to_csv(
        r"Insumos\Universo_Directa_Resultado.csv",
        index=False,
        encoding="utf-8",
    )

    # INDIRECTA
    df_u_indirecta.to_excel(
        r"Insumos\Universo_Indirecta_Resultado.xlsx",
        index=False,
    )

    df_u_indirecta.to_csv(
        r"Insumos\Universo_Indirecta_Resultado.csv",
        index=False,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
