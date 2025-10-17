import yaml
from Utils.general_functions import logger
from typing import Any, Dict


def load_config(
    nom_archivo_configuracion: str = "Controllers/setting/config.yml",
) -> dict[str, Any]:
    """
    Lee un archivo YAML de configuración para un proyecto.

    Args:
        nom_archivo_configuracion (str): Ruta del archivo YAML que contiene
            la configuración del proyecto.

    Returns:
        dict: Diccionario con la información de configuración cargada.
    """
    try:
        with open(nom_archivo_configuracion, "r", encoding="utf-8") as ymlfile:
            configuracion = yaml.safe_load(ymlfile)
        logger.info("Proceso de obtención de configuración satisfactorio")
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}")
        raise e

    return configuracion
