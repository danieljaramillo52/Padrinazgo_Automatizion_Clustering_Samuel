# Pasos para crear un método.
import pandas as pd
from typing import List
from loguru import logger

"""
1. Definición de la función: Nombre alusivo y referente a la funcionalidad
    funciones y métodos : snake_case

    Aplicar_regla_Negocio_Socio => regla_negocio_socio.

    Clase: CamelCase

2. parametros de la función Tipados preferiblemente con la libreria Typing.
    def eliminar_duplicados_df(df: pd.DataFrame, col_ref: str | list[str]) -> pd.DataFrame:
    list[str] != List[str]

    list => Clase
    List => Tipo de dato lista.

3. Docstring adecuado: 
    '''
    Descripción de la función / utilidad de manera breve. 
    
    Args: 
        Parametros de la función: 
        df (pd.Dataframe): Dataframe de pandas donde se aplica la transformación. 
        cliente_col (str) : Columna sobre la que se aplica la trnasofación
        marca_col (columna) 
    Retruns: obj : Que retorna la función.  
"""

"""Principos solid: 
    1. PRU : Principio de Responsabilidad Única.
    
    renombrar columnas : Bien
    selecionar columnas : Bien
    filtrar columnas : Bien
    leer_archivo: Bien 
    validar y leer archivo: (mal a medias porque la lectura de una validación es mínima). Lee no más de 1000 registros. 
    renombrar y sleccionar : Mal 
    
    """


def limpiar_datos_ventas(
    df: pd.DataFrame, cliente_col: str, marca_col: str
) -> pd.DataFrame:
    """Limpia y normaliza columnas clave de ventas."""
    df = df.copy()
    df[cliente_col] = df[cliente_col].astype(str).str.strip()
    df[marca_col] = df[marca_col].astype(str).str.strip()
    return df.dropna(subset=[cliente_col, marca_col])


def normalizar_col_pd(
    df: pd.DataFrame, cols_normalizar: str | List[str]
) -> pd.DataFrame:
    """
    Limpia y normaliza columnas de texto en un DataFrame, eliminando espacios
    en blanco y asegurando tipo `str`.

    Si se proporciona una lista de columnas, aplica la normalización a cada una.
    En caso de error (columna inexistente, tipo no compatible, etc.), se captura
    la excepción y se registra el fallo sin interrumpir el flujo del programa.

    Args:
        df (pd.DataFrame): DataFrame sobre el que se aplica la transformación.
        cols_normalizar (str | List[str]): Columna o lista de columnas a normalizar.

    Returns:
        pd.DataFrame: DataFrame con las columnas transformadas. Si ocurre un error,
        se devuelve el DataFrame original sin cambios.

    Example:
        >>> df = normalizar_col_pd(df=df, cols_normalizar=["Cliente", "Producto"])
    """
    try:
        df = df.copy()
        # Si es un solo nombre de columna, conviértelo a lista
        if isinstance(cols_normalizar, str):
            cols_normalizar = [cols_normalizar]

        # Aplicar normalización
        df[cols_normalizar] = (
            df[cols_normalizar].astype(str).apply(lambda col: col.str.strip())
        )

        logger.info(f" Normalización exitosa en columnas: {cols_normalizar}")
        return df

    except Exception as e:
        logger.error(f"Error al normalizar columnas {cols_normalizar}: {e}")
        return df
