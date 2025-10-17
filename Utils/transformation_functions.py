import pandas as pd
from Utils.general_functions import logger


def eliminar_duplicados_df(df: pd.DataFrame, col_ref: str | list[str]) -> pd.DataFrame:
    """Elimina filas duplicadas según columnas de referencia."""
    inicial = len(df)
    df_sin_duplicados = df.drop_duplicates(subset=col_ref, keep="first")
    eliminados = inicial - len(df_sin_duplicados)
    logger.info(f"Eliminados {eliminados} duplicados basados en {col_ref}")
    return df_sin_duplicados


def limpiar_datos_ventas(df: pd.DataFrame, cliente_col: str, marca_col: str) -> pd.DataFrame:
    """Limpia y normaliza columnas clave de ventas."""
    df = df.copy()
    df[cliente_col] = df[cliente_col].astype(str).str.strip()
    df[marca_col] = df[marca_col].astype(str).str.strip()
    return df.dropna(subset=[cliente_col, marca_col])


def agregar_ventas_por_cliente_y_marca(
    ventas_df: pd.DataFrame,
    cliente_col: str = "Cliente",
    marca_col: str = "Marca",
    pesos_col: str = "Venta $",
    kg_col: str = "Venta Kg",
    start_year: int | None = None,
    end_year: int | None = None,
    start_month: int | None = None,
    end_month: int | None = None,
) -> pd.DataFrame:
    """
    Agrega ventas por cliente y marca, crea columnas pivotadas y calcula promedios.
    """
    df = limpiar_datos_ventas(ventas_df, cliente_col, marca_col)

    for col in [pesos_col, kg_col]:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

    grp = df.groupby([cliente_col, marca_col], dropna=False).agg(
        ventas_pesos=(pesos_col, "sum"),
        ventas_kg=(kg_col, "sum"),
    ).reset_index()

    pivot_pesos = grp.pivot_table(index=cliente_col, columns=marca_col, values="ventas_pesos", fill_value=0)
    pivot_kg = grp.pivot_table(index=cliente_col, columns=marca_col, values="ventas_kg", fill_value=0)

    pivot_pesos.columns = [f"ventas_{str(c).strip().lower().replace(' ', '_')}_pesos" for c in pivot_pesos.columns]
    pivot_kg.columns = [f"ventas_{str(c).strip().lower().replace(' ', '_')}_kg" for c in pivot_kg.columns]

    totales = df.groupby(cliente_col).agg(total_pesos=(pesos_col, "sum"), total_kg=(kg_col, "sum"))

    resultado = totales.join(pivot_pesos, how="left").join(pivot_kg, how="left").fillna(0)

    if all(v is not None for v in [start_year, end_year, start_month, end_month]):
        start_date = pd.Timestamp(start_year, start_month, 1)
        end_date = pd.Timestamp(end_year, end_month, 1)
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
        months = max(1, months)
        logger.info(
            f"Calculando promedios mensuales usando periodo {start_date.strftime('%Y-%m')} - "
            f"{end_date.strftime('%Y-%m')} ({months} meses)."
        )
    else:
        months = 1
        logger.warning("Periodo no definido, se asumirá 1 mes.")

    resultado["promedio_pesos_periodo"] = resultado["total_pesos"] / months
    resultado["promedio_kg_periodo"] = resultado["total_kg"] / months

    resultado = resultado.reset_index().rename(columns={cliente_col: "cliente"})
    logger.info("Agregación y cálculo de promedios completado.")
    return resultado


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

    merged = df.merge(ventas, how=how, left_on=universo_cliente_col, right_on=ventas_cliente_col)
    logger.info(f"Merge entre universo ({len(df)}) y ventas ({len(ventas)}). Resultado: {len(merged)} filas.")
    return merged
