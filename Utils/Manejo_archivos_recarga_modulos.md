# Inspeccionar archivos y modulos. 

1. Recargar modulo: 

```python
import importlib # Libreria para tratabajar con módulos


importlib.reload(modulo) # Recargar modulo sin necesiada de volver a correr.

"""
Ejemplo:

Utils.general_functions as gf
Utils.transformation_functions as tf 
importlib.reload(gf)

importlib.reload(tf)
"""

# Utilidad: Me permite actualizar el contenido de cualquier modulo sin volver a ejecutar el programa principal desde el principio
```

2. Consultar ```name_space`` de un modulo. 

```python
dir(modulo) (Previamente importado)

"""
Ejemplo: 
dir(general_functions) / dir(tf). 
"""

# Utilidad: Me permite ver los nombres todas las clases, métodos y funciones de un modulo de python sin necesidad de entrar directamente. 
```

3. Revisar el contenido de un método o modulo especifico 

```python
import inspect

print(inspect.getsource(gf.leer_excel_columnas))
```