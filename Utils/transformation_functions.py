import pandas as pd
from typing import Iterable, Union, List

ColLike = Union[str, int]

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
) -> pd.DataFrame:

    df_concatenado = pd.concat(dataframes, ignore_index=True)

    return df_concatenado


def to_numeric_cols(
    df: pd.DataFrame,
    cols: Union[ColLike, Iterable[ColLike]],
    *,
    errors: str = "coerce",
    inplace: bool = True,
) -> pd.DataFrame:
    """
    Convierte a numérico una o varias columnas existentes.
    - No hace ninguna normalización/limpieza.
    - Ignora columnas inexistentes.

    Args:
        df: DataFrame de entrada.
        cols: Nombre(s) de columna(s) a convertir (str, int o iterable).
        errors: parámetro de pd.to_numeric ('coerce'|'raise'|'ignore').
        inplace: si True modifica df; si False devuelve copia.

    Returns:
        DataFrame modificado (o copia si inplace=False).
    """
    if isinstance(cols, (str, int)):
        cols = [cols]

    cols_presentes = [c for c in cols if c in df.columns]
    work = df if inplace else df.copy()
    if cols_presentes:
        work[cols_presentes] = work[cols_presentes].apply(pd.to_numeric, errors=errors)
    return work


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
) -> pd.DataFrame:

    df_concatenado = pd.concat(dataframes, ignore_index=True)

    return df_concatenado


def cambiar_formato_indirecta(ruta_archivo):
    """
    Procesa el archivo de ventas indirectas y retorna un DataFrame normalizado.

    Args:
        ruta_archivo (str): Ruta del archivo Excel de ventas indirectas

    Returns:
        pd.DataFrame: DataFrame con columnas [Agente Comercial, Código ECOM, Mes, Marca, Venta $, Venta Kg]
    """
    try:
        # Leer archivo
        df_vts_ind = pd.read_excel(ruta_archivo)
        logger.info(f"Archivo leído correctamente: {ruta_archivo}")

        # Renombrar columnas principales
        df_vts_ind = df_vts_ind.rename(
            columns={
                "Unnamed: 0": "Agente Comercial",
                "Unnamed: 1": "Código ECOM",
                "Unnamed: 2": "Marca",
            },
            inplace=False,
        )

        # Identificar columnas de COP y KG
        columnas_cop = {}
        columnas_kg = {}

        for col in df_vts_ind.columns:
            if col not in ["Agente Comercial", "Código ECOM", "Marca"]:
                tipo = df_vts_ind[col].iloc[1]
                mes = df_vts_ind[col].iloc[0]

                if tipo == "COP":
                    columnas_cop[col] = mes
                elif tipo == "KG":
                    columnas_kg[col] = mes

        # Eliminar las primeras 2 filas de encabezados
        df_vts_ind = df_vts_ind.iloc[2:].reset_index(drop=True)

        # Procesar columnas COP
        df_vtas_cop = df_vts_ind[
            ["Agente Comercial", "Código ECOM", "Marca"] + list(columnas_cop.keys())
        ]
        df_vtas_cop.rename(columns=columnas_cop, inplace=True)

        meses_cop = list(columnas_cop.values())
        df_cop = df_vtas_cop[
            ["Agente Comercial", "Código ECOM", "Marca"] + meses_cop
        ].melt(
            id_vars=["Agente Comercial", "Código ECOM", "Marca"],
            var_name="Mes",
            value_name="Venta $",
        )

        # Procesar columnas KG
        df_vtas_kg = df_vts_ind[
            ["Agente Comercial", "Código ECOM", "Marca"] + list(columnas_kg.keys())
        ]
        df_vtas_kg.rename(columns=columnas_kg, inplace=True)

        meses_kg = list(columnas_kg.values())
        df_kg = df_vtas_kg[
            ["Agente Comercial", "Código ECOM", "Marca"] + meses_kg
        ].melt(
            id_vars=["Agente Comercial", "Código ECOM", "Marca"],
            var_name="Mes",
            value_name="Venta Kg",
        )

        # Merge de COP y KG
        df_final = pd.merge(
            df_cop, df_kg, on=["Agente Comercial", "Código ECOM", "Mes", "Marca"]
        )
        df_final = df_final[
            ["Agente Comercial", "Código ECOM", "Mes", "Marca", "Venta $", "Venta Kg"]
        ]

        logger.info("Procesamiento de ventas indirectas completado con éxito")
        return df_final

    except FileNotFoundError:
        logger.error(f"Archivo no encontrado: {ruta_archivo}")
        raise
    except KeyError as e:
        logger.error(f"Error: Columna esperada no encontrada - {e}")
        raise
    except Exception as e:
        logger.error(f"Error en el procesamiento de ventas indirectas: {e}")
        raise


def cambiar_ventas_por_marca(df_dic_prub):
    """
    Procesa ventas directas agrupando por cliente y calculando totales por marca.

    Args:
        df_dic_prub (pd.DataFrame): DataFrame con columnas [Cliente, Mes, Marca, Venta $, Venta Kg]

    Returns:
        pd.DataFrame: DataFrame con totales de ventas por marca para cada cliente
    """

    try:
        df_dic_prub["Venta $"] = pd.to_numeric(df_dic_prub["Venta $"], errors="coerce")
        df_dic_prub["Venta Kg"] = pd.to_numeric(
            df_dic_prub["Venta Kg"], errors="coerce"
        )

        marcas = df_dic_prub["Marca"].unique()
        df_resutado_prub = df_dic_prub.copy()

        if "Cliente" in df_dic_prub.columns:
            columna_agrupacion = "Cliente"
        else:
            columna_agrupacion = "Agente Comercial"

        for marca in marcas:
            sum_marca = (
                df_dic_prub[df_dic_prub["Marca"] == marca]
                .groupby(columna_agrupacion)[["Venta $", "Venta Kg"]]
                .sum()
            )
            sum_marca.columns = [f"v$ {marca}", f"vKg {marca}"]
            df_resutado_prub = df_resutado_prub.merge(
                sum_marca, on=columna_agrupacion, how="left"
            )

        df_resutado_prub = df_resutado_prub.fillna(0)
        df_resutado_prub = df_resutado_prub.drop(
            columns=["Marca", "Venta $", "Venta Kg"]
        )

        logger.info("se realizo con exito el cambio de formato")
        return df_resutado_prub

    except Exception as e:
        logger.error(f"Error en el cambio de formato: {e}")
        raise


from pandas import DataFrame


class CambiarVtasMarca:
    MARCA = "Marca"
    VENTA_COP = "Venta $"
    VENTA_KG = "Venta Kg"

    def __init__(self, df: DataFrame):
        self.df = df

    def ejectuar_proceso(self):
        """Encapsula la ejecución del proceso para agregar las ventas por marca en pesos y kilos."""

        # Tratar valores de vtas a numericos
        df = to_numeric_cols(df=df, cols=[self.VENTA_COP, self.VENTA_KG], inplace=False)

        # Extraer marcas únicas
        marcas = df[self.MARCA].unique()
        df_copy = df.copy()

        # Tratar ventas nulas.
        df_copy[[self.VENTA_COP, self.VENTA_KG]] = df_copy[
            [self.VENTA_COP, self.VENTA_KG]
        ].fillna(0)

        if "Cliente" in df.columns:
            columna_agrupacion = "Cliente"
        else:
            columna_agrupacion = ["Agente Comercial", "Código ECOM"]
