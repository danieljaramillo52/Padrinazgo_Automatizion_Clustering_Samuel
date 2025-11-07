from loguru import logger
import yaml
import os
from typing import Dict, List
import pandas as pd
from pathlib import Path
import sys

logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
)


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


def validar_dir(path) -> bool:
    if not os.path.exists(path):
        logger.error(f"El directorio '{path}' no existe")
        return False

    if not os.path.isdir(path):
        logger.error(f"'{path}' no es un directorio")
        return False

    logger.info(f"'{path}' existe y es un directorio válido")
    return True


def leer_excel_columnas(
    ruta: str,
    sheet_name: str = 0,
    columnas: list = None,
    dtype: str = None,
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
            f"lectura completada con exito. "
            f"Filas: {len(df)}, Columnas: {len(df.columns)}"
        )

        return df

    except FileNotFoundError:
        logger.error(f"ERROR en lectura: Archivo no encontrado en {ruta}")
        return None
    except KeyError as e:
        logger.error(f"ERROR en lectura: Columna no existe - {str(e)}")
        return None
    except Exception as e:
        logger.error(f"ERROR en lectura: {str(e)}")
        return None


def exportar_a_excel(
    ruta_archivo: str, df: pd.DataFrame, nom_hoja: str = "Hoja1", index: bool = False
) -> str:
    """
    Exporta un DataFrame a un archivo Excel o CSV según la extensión.
    Si la carpeta destino no existe, se crea automáticamente.

    Args:
        ruta_archivo (str): Ruta completa del archivo (incluye el nombre y extensión .xlsx o .csv).
        df (pd.DataFrame): DataFrame a exportar.
        nom_hoja (str): Nombre de la hoja dentro del archivo (solo para Excel).
        index (bool): Si se incluye o no el índice.

    Returns:
        str: Mensaje de éxito para el log.
    """
    try:
        ruta = Path(ruta_archivo)

        # Crear carpeta si no existe
        ruta.parent.mkdir(parents=True, exist_ok=True)

        # Exportar según extensión
        if ruta.suffix.lower() == ".csv":
            df.to_csv(ruta, index=index)
            logger.info(
                f"✅ Exportación CSV completada: '{ruta.name}' en '{ruta.parent}'"
            )
        else:
            df.to_excel(ruta, sheet_name=nom_hoja, index=index)
            logger.info(
                f"✅ Exportación Excel completada: '{ruta.name}' con hoja '{nom_hoja}' en '{ruta.parent}'"
            )

        return f"✅ Exportación completada: '{ruta.name}' en '{ruta.parent}'"

    except Exception as e:
        logger.error(f"❌ Error exportando '{ruta_archivo}': {e}")
        raise


def leer_excels_dir(
    ruta: str,
    patron: str = None,
    dtype: str = None,
) -> List[pd.DataFrame]:

    if not validar_dir(ruta):
        return

    archivos = sorted(
        [
            os.path.join(ruta, f)
            for f in os.listdir(ruta)
            if patron is None or f.lower().endswith(patron)
        ]
    )

    dataframes = []

    for archivo in archivos:
        try:
            df = leer_excel_columnas(archivo, dtype=dtype)
            dataframes.append(df)
        except Exception as e:
            raise Exception(f"Error precesando '{archivo}': {e}")

    if not dataframes:
        raise ValueError("No se pudo leer ningún archivo exitosamente")

    return dataframes
