from loguru import logger
import yaml
import os
import pandas as pd 


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
def Validar_Archivos():
    
    """
    Valida que todos los archivos requeridos existan en las rutas especificadas.
    Usa try/except para capturar errores al acceder a los archivos.
    
    Retorna:
    --------
    bool
        True si todos los archivos existen, False si falta alguno.
    """


    for archivo in archivos:
        if not os.path.exists(archivo):
            logger.error(f"ERROR: {archivo}")
        else:
            logger.info(f"Ok {archivo}")


def leer_excel_columnas(
    ruta: str,
    sheet_name: str = 0,
    columnas: list = None,
    dtype: str = None,
    nombre_lectura: str = "lectura"
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
            f"{nombre_lectura} completada. "
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