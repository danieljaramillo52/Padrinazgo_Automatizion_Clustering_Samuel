from loguru import logger
import yaml
import os
from typing import Dict, List
import pandas as pd
from pathlib import Path


def procesar_configuracion(nom_archivo_configuracion: str) -> dict:
    """Lee un archivo YAML de configuración para un proyecto.

    Args:
        nom_archivo_configuracion (str): Nombre del archivo YAML que contiene
            la configuración del proyecto.

    Returns:
        dict: Un diccionario con la información de configuración leída del archivo YAML.
    """
    try:
        with open(nom_archivo_configuracion, "r", encoding="utf-8") as archivo:
            configuracion_yaml = yaml.safe_load(archivo)
        logger.success("Proceso de obtención de configuración satisfactorio")
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}")
        raise e

    return configuracion_yaml


archivos = [
    r"Insumos\Universo Directa.xlsm",
    r"Insumos\Universo Indirecta.xlsm",
    r"Insumos\BaseSocios.xlsm",
    r"Insumos\DriverCoordenadas.xlsx",
]


def validar_archivos(archivos: Dict[str, str]):
    """
    Valida que todos los archivos requeridos existan en las rutas especificadas.
    Usa try/except para capturar errores al acceder a los archivos.

    Retorna:
    --------
    bool
        True si todos los archivos existen, False si falta alguno.
    """

    for archivo, path_archivo in archivos.items():
        if not os.path.exists(path_archivo):
            logger.error(
                f"ERROR: {archivo} archivo no presente en el directorio insumos"
            )
        else:
            logger.info(f"Ok: {archivo} encontrado correctamente")


def leer_excel_columnas(
    ruta: str,
    sheet_name: str = 0,
    columnas: list = None,
    dtype: str = None,
    nombre_lectura: str = "lectura",
) -> pd.DataFrame:

    try:

        params = {
            "sheet_name": sheet_name,
        }

        # Agregar columnas si se especifican
        if columnas is not None:
            params["usecols"] = columnas

        if dtype is not None:
            params["dtype"] = dtype

        df = pd.read_excel(ruta, **params)

        logger.info(
            f"{nombre_lectura} completada con exito. "
            f"Filas: {len(df)}, Columnas: {len(df.columns)}"
        )

        return df

    except FileNotFoundError:
        logger.error(f"ERROR en {nombre_lectura}: Archivo no encontrado en {ruta}")
        return None
    except KeyError as e:
        logger.error(f"ERROR en {nombre_lectura}: Columna no existe - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"ERROR en {nombre_lectura}: {str(e)}")
        return None


def exportar_a_excel(
    ruta_archivo: str, df: pd.DataFrame, nom_hoja: str = "Hoja1", index: bool = False
) -> str:
    """
    Exporta un DataFrame a un archivo Excel en la ruta completa especificada.
    Si la carpeta destino no existe, se crea automáticamente.

    Args:
        ruta_archivo (str): Ruta completa del archivo (incluye el nombre y extensión .xlsx).
        df (pd.DataFrame): DataFrame a exportar.
        nom_hoja (str): Nombre de la hoja dentro del archivo.
        index (bool): Si se incluye o no el índice.

    Returns:
        str: Mensaje de éxito para el log.
    """
    try:
        ruta = Path(ruta_archivo)

        # Crear carpeta si no existe
        ruta.parent.mkdir(parents=True, exist_ok=True)

        # Exportar el DataFrame
        df.to_excel(ruta, sheet_name=nom_hoja, index=index)

        return f"✅ Exportación completada: '{ruta.name}' con hoja '{nom_hoja}' en '{ruta.parent}'"

    except Exception as e:
        logger.error(f"❌ Error exportando '{ruta_archivo}': {e}")
        raise



def leer_excel_directa  (
    ruta: str,
    patron: str = "*.xlsx",
    dtype: str = None,
   
) -> List[pd.DataFrame]:
    

    if not os.path.exists(ruta):  
        raise FileNotFoundError(f"El directorio '{ruta}' no existe")
    
    if not os.path.isdir(ruta):  # ✅ Usar os.path
        raise NotADirectoryError(f"'{ruta}' no es un directorio")
    
    extension = patron.replace("*", "")

    archivos = sorted([
        os.path.join(ruta, f)
        for f in os.listdir(ruta)
        if f.lower().endswith(extension)  
    ])

    dataframes = []

    for archivo in archivos:
        try:
            df = pd.read_excel(archivo, dtype=str)
            dataframes.append(df)
        except Exception as e:
            raise Exception(f"Error precesando '{archivo}': {e}")
        
    if not dataframes:
        raise ValueError("No se pudo leer ningún archivo exitosamente")
    
    return dataframes
            



