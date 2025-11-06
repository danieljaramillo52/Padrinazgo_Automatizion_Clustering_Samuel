import pandas as pd
from typing import List

# from Utils.general_functions import logger
import logging

logger = logging.getLogger(__name__)


def eliminar_duplicados_df(df: pd.DataFrame, col_ref: str | list[str]) -> pd.DataFrame:
    """Elimina filas duplicadas según columnas de referencia."""
    df_sin_duplicados = df.drop_duplicates(subset=col_ref, keep="first")
    return df_sin_duplicados


def limpiar_datos_ventas(
    df: pd.DataFrame, cliente_col: str, marca_col: str
) -> pd.DataFrame:
    """Limpia y normaliza columnas clave de ventas."""
    df = df.copy()
    df[cliente_col] = df[cliente_col].astype(str).str.strip()
    df[marca_col] = df[marca_col].astype(str).str.strip()
    return df.dropna(subset=[cliente_col, marca_col])


def eliminar_duplicados_serie(serie: pd.Series, keep: str = "first") -> pd.Series:
    """
    Elimina valores duplicados de una serie de pandas y registra el resultado.

    Esta función elimina los valores duplicados de una `pd.Series`,
    conservando por defecto la primera ocurrencia de cada valor.
    Registra un mensaje de éxito si se eliminan duplicados o de
    advertencia si no se detecta ninguno.

    Args:
        serie (pd.Series): Serie sobre la cual se eliminarán los duplicados.
        keep (str, opcional): Estrategia de conservación. Puede ser:
            - "first": conserva la primera ocurrencia (por defecto).
            - "last": conserva la última ocurrencia.
            - False: elimina todas las ocurrencias duplicadas.

    Returns:
        pd.Series: Serie resultante sin valores duplicados.
    """
    longitud_inicial = len(serie)
    serie_sin_duplicados = serie.drop_duplicates(keep=keep)
    eliminados = longitud_inicial - len(serie_sin_duplicados)

    if eliminados > 0:
        logger.info(f"Se eliminaron {eliminados} valores duplicados de la serie.")
    else:
        logger.warning(
            "No se detectaron duplicados en la serie; no se realizaron cambios."
        )

    return serie_sin_duplicados




def merge_ventas_con_universo(
    universo_df: pd.DataFrame,
    ventas_agg_df: pd.DataFrame,
    universo_cliente_col: str,
    ventas_cliente_col: str = "cliente",
    how: str = "left",
) -> pd.DataFrame:
    """Realiza merge entre universo y ventas agregadas."""
    df = universo_df.copy()
    ventas = ventas_agg_df.copy()

    df[universo_cliente_col] = df[universo_cliente_col].astype(str).str.strip()
    ventas[ventas_cliente_col] = ventas[ventas_cliente_col].astype(str).str.strip()

    merged = df.merge(
        ventas, how=how, left_on=universo_cliente_col, right_on=ventas_cliente_col
    )
    logger.info(
        f"Merge entre universo ({len(df)}) y ventas ({len(ventas)}). Resultado: {len(merged)} filas."
    )
    return merged


def Aplicar_Regla_Negocio_Z1_ZA(
    
    df_resultado: pd.DataFrame,
    cliente_col: str = "Cód. Cliente",
    z1_col: str = "Cod_vend Z1",
    za_col: str = "Cod_vend ZA",
) -> pd.DataFrame:
    

    """
    Aplica regla de negocio que elimina vendedores ZA cuando existe vendedor Z1.
    
    Si un cliente tiene asignado un vendedor Z1, se elimina el vendedor ZA asociado,
    priorizando la venta Z1 sobre la ZA.
    
    Parámetros:
    -----------
    df_resultado : pd.DataFrame
        DataFrame con información de clientes y vendedores.
        
    cliente_col : str, optional
        Nombre de la columna que contiene el ID del cliente.
        Por defecto: "Cód. Cliente"
        
    z1_col : str, optional
        Nombre de la columna que contiene el código del vendedor Z1.
        Por defecto: "Cod_vend Z1"
        
    za_col : str, optional
        Nombre de la columna que contiene el código del vendedor ZA.
        Por defecto: "Cod_vend ZA"
    
    Retorna:
    --------
    pd.DataFrame
        DataFrame con la regla de negocio aplicada. Los vendedores ZA se establecen
        en None cuando existe un vendedor Z1 para el mismo cliente.
    
    Lógica:
    -------
    1. Identifica todos los clientes que tienen vendedor Z1 asignado (no nulo)
    2. Para esos clientes, elimina el vendedor ZA (lo pone en None)
    3. Los clientes sin vendedor Z1 mantienen su vendedor ZA
    
    Ejemplo:
    --------
     df = pd.DataFrame({
         'Cód. Cliente': [1, 2, 3],
        'Cod_vend Z1': [101, None, 102],
         'Cod_vend ZA': [201, 202, 203]
     })
        resultado = Aplicar_Regla_Negocio_Z1_ZA(df)
        resultado['Cod_vend ZA'].tolist()
        [None, 202, None]
    
    Notas:
    ------
    - La función crea una copia del DataFrame, no modifica el original
    - Solo afecta la columna ZA cuando hay Z1 presente
    - Los valores nulos en Z1 se respetan y no afectan a ZA
    """

    df_resultado = df_resultado.copy()

    hay_z1 = df_resultado[z1_col].notna()
    df_resultado.loc[hay_z1, za_col] = None  # Eliminar fila

    return df_resultado


def Aplicar_regla_Negocio_Socio(
    df_resultado: pd.DataFrame, z1_col: str = "Cod_vend Z1", za_col: str = "Cod_vend ZA"
) -> pd.DataFrame:
    

    """
    Aplica regla de negocio para clasificar clientes como socios o no socios.
    
    Primero aplica la regla Z1_ZA (elimina ZA si existe Z1), luego clasifica
    cada cliente como "SI" (es socio) o "NO" (no es socio) basado en si tiene
    vendedor Z1 o ZA asignado.
    
    Parámetros:
    -----------
    df_resultado : pd.DataFrame
        DataFrame con información de clientes y vendedores.
        
    z1_col : str, optional
        Nombre de la columna que contiene el código del vendedor Z1.
        Por defecto: "Cod_vend Z1"
        
    za_col : str, optional
        Nombre de la columna que contiene el código del vendedor ZA.
        Por defecto: "Cod_vend ZA"
    
    Retorna:
    --------
    pd.DataFrame
        DataFrame con nueva columna "Col_Socio" que indica si el cliente es socio.
        Valores: "SI" (tiene Z1 o ZA) o "NO" (no tiene ninguno).
    
    Lógica:
    -------
    1. Aplica Aplicar_Regla_Negocio_Z1_ZA() para priorizar Z1 sobre ZA
    2. Identifica clientes con Z1 asignado
    3. Identifica clientes con ZA asignado
    4. Marca como "SI" si tiene Z1 O ZA (al menos uno)
    5. Marca como "NO" si no tiene ni Z1 ni ZA
    
    Ejemplo:
    --------
    df = pd.DataFrame({
         'Cod_vend Z1': [101, None, None],
         'Cod_vend ZA': [None, 202, None]
     })
     resultado = Aplicar_regla_Negocio_Socio(df)
     resultado['Col_Socio'].tolist()
    ['SI', 'SI', 'NO']
    
    Notas:
    ------
    - La función crea una copia del DataFrame, no modifica el original
    - Un cliente es socio si tiene Z1, ZA, o ambos
    - Un cliente NO es socio solo si no tiene Z1 ni ZA
    """

    df_resultado = df_resultado.copy()

    df_resultado = Aplicar_Regla_Negocio_Z1_ZA(df_resultado, z1_col, za_col)

    tiene_z1 = df_resultado[z1_col].notna()
    tiene_za = df_resultado[za_col].notna()

    df_resultado["Col_Socio"] = "NO"
    df_resultado.loc[tiene_z1 | tiene_za, "Col_Socio"] = "SI"

    return df_resultado


def concatenar_columnas_pd(
    df: pd.DataFrame,
    cols_elegidas: List[str],
    nueva_columna: str,
    usar_separador: bool = False,  # 🔹 Nuevo parámetro opcional (False por defecto)
    separador: str = " : ",  # 🔹 Separador por defecto (espacio)
) -> pd.DataFrame:
    """
    Concatena las columnas especificadas y agrega el resultado como una nueva columna al DataFrame.

    Parámetros:
    - dataframe (pd.DataFrame): DataFrame del cual se concatenarán las columnas.
    - cols_elegidas (list): Lista de nombres de las columnas a concatenar.
    - nueva_columna (str): Nombre de la nueva columna que contendrá el resultado de la concatenación.
    - usar_separador (bool): Si es True, concatena las columnas con el separador definido en 'separador'.
    - separador (str): Caracter usado para separar las columnas concatenadas (por defecto, espacio).

    Retorna:
    - pd.DataFrame: DataFrame con la nueva columna agregada.
    """
    try:
        # Verificar si dataframe es un DataFrame de pandas
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El argumento 'dataframe' debe ser un DataFrame de pandas.")

        # Verificar si las columnas especificadas existen en el DataFrame
        for col in cols_elegidas:
            if col not in df.columns:
                raise KeyError(f"La columna '{col}' no existe en el DataFrame.")

        df_copy = df.copy()

        # 🔹 Si usar_separador es True, concatenar con separador. Si no, concatenar normal.
        if usar_separador:
            df_copy.loc[:, nueva_columna] = (
                df_copy[cols_elegidas].fillna("").agg(separador.join, axis=1)
            )
        else:
            df_copy.loc[:, nueva_columna] = (
                df_copy[cols_elegidas].fillna("").agg("".join, axis=1)
            )

        # Registrar el proceso
        logger.info(
            f"Columnas '{', '.join(cols_elegidas)}' concatenadas {'con separador' if usar_separador else 'sin separador'} y almacenadas en '{nueva_columna}'."
        )

        return df_copy

    except Exception as e:
        logger.error(f"Error en la concatenación de columnas: {e}")
        return df


def concatenar_vertical(
        dataframes: List,

)-> pd.DataFrame:

    df_concatenado = pd.concat(dataframes, ignore_index=True)


    return df_concatenado