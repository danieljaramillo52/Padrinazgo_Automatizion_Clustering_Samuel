import sys
import os
import pandas as pd
import config_path_routes
from Utils import general_functions as gf
from Utils import Aplicar_Regla_Negocio_Z1_ZA, Aplicar_regla_Negocio_Socio

archivos = [
    r"Insumos\Universo Directa.xlsm",
    r"Insumos\Universo Indirecta.xlsm",
    r"Insumos\BaseSocios.xlsm",
    r"Insumos\DriverCoordenadas.xlsx", 
]


def main():
    config = gf.procesar_configuracion(
        nom_archivo_configuracion="Controllers/setting/config.yml"
    )
    pd.read_excel(config["Insumos"]["path_insumos"] + config["Insumos"]universo_directa)

    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"ERROR: {archivo}")
        else:
            print(f"Ok {archivo}")

    df_u_directa = pd.read_excel(
        r"Insumos\Universo Directa.xlsm",
        sheet_name="Maestra",
        dtype=str,
        usecols="A:G,W",
    )

    # print(df_u_directa)
    # print("----------------------------")   #Mostrar las tablas de tabla completa
    # print(df_u_directa.columns)

    # print(df_u_directa)
    # print("----------------------------")
    # print(df_u_directa.columns)

    # print(df_u_indirecta)

    df_Bas_Socio = pd.read_excel(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\BaseSocios.xlsm"
    )

    # print("Base de socios")
    # print(df_Bas_Socio.columns)

    columnas_socios = [
        "Atención",
        "Tipo Socios",
        "Cod_vend Z1",
        "Nom_Vend Z1",
        "Cod_vend ZA",
        "Nom_Vend ZA",
    ]

    df_u_directa["Cód. Cliente"] = df_u_directa["Cód. Cliente"].astype(str)
    df_Bas_Socio["Cod_Cliente"] = df_Bas_Socio["Cod_Cliente"].astype(str)

    df_u_directa_completa_Socios = df_u_directa.merge(
        df_Bas_Socio[["Cod_Cliente"] + columnas_socios],
        left_on="Cód. Cliente",
        right_on="Cod_Cliente",  # eliminar duplicados antes
        how="left",
    )

    # print(df_u_indirecta_completa_socios)
    # print("coincidencias")
    # print(df_u_indirecta_completa[df_u_indirecta_completa['Cod_vend Z1'].notna()].head(10))

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(
        subset="Cód. Cliente", keep="first"
    )

    # print(df_u_directa_completa_Socios['Cod_vend Z1'].dtype)
    # print(df_u_directa_completa_Socios.columns)

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

    # print(df_u_directa_completa_Socios)

    # print(df_u_indirecta.columns)

    # df_u_directa_completa_Socios = df_u_indirecta.merge()

    df_u_indirecta = pd.read_excel(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo Indirecta.xlsm",
        dtype=str,
    )

    df_coord = pd.read_excel(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\DriverCoordenadas.xlsx",
        dtype=str,
        sheet_name="Base",
    )

    # print(df_driver_coordenadas.columns)
    # print(df_driver_coordenadas)

    df_coord_dir = df_coord[df_coord["Agente Comercial"].isnull()][
        ["Cliente", "Grado latitud", "Grad.long."]
    ]
    df_coord_ind = df_coord[~df_coord["Agente Comercial"].isnull()][
        ["Agente Comercial", "Código ECOM", "Grado latitud", "Grad.long."]
    ]

    df_u_directa_completa_Socios = df_u_directa_completa_Socios.merge(
        df_coord_dir, left_on="Cód. Cliente", right_on="Cliente", how="left"
    )

    df_u_indirecta["llave_compuesta"] = (
        df_u_indirecta["r_id_agente_comercial"].astype(str)
        + "_"
        + df_u_indirecta["r_id_cliente"].astype(str)
    )

    df_coord_ind["llave_compuesta"] = (
        df_coord_ind["Agente Comercial"].astype(str)
        + "_"
        + df_coord_ind["Código ECOM"].astype(str)
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
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo_Directa_Resultado.xlsx",
        index=False,
    )

    df_u_directa_completa_Socios.to_csv(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo_Directa_Resultado.csv",
        index=False,
        encoding="utf-8",
    )

    # INDIRECTA
    df_u_indirecta.to_excel(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo_Indirecta_Resultado.xlsx",
        index=False,
    )

    df_u_indirecta.to_csv(
        r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo_Indirecta_Resultado.csv",
        index=False,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
