import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import pandas as pd 
from Utils import Aplicar_Regla_Negocio_Z1_ZA, Aplicar_regla_Negocio_Socio



df_u_directa = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo Directa.xlsm",
                             sheet_name = "Maestra")
#print(df_u_directa)
#print("----------------------------")   #Mostrar las tablas de tabla completa
#print(df_u_directa.columns)

df_u_directa = df_u_directa.iloc[:, list(range(7)) + [22]]

#print(df_u_directa)
#print("----------------------------")
#print(df_u_directa.columns)

df_u_indirecta = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo Indirecta.xlsm")

#print(df_u_indirecta)

df_Bas_Socio = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\BaseSocios.xlsm")

#print("Base de socios")
#print(df_Bas_Socio.columns)

columnas_socios = ['Atención', 'Tipo Socios', 'Cod_vend Z1', 'Nom_Vend Z1', 'Cod_vend ZA',
       'Nom_Vend ZA',]

df_u_directa_completa_Socios = df_u_directa.merge(
    df_Bas_Socio[['Cod_Cliente'] + columnas_socios],
     left_on='Cód. Cliente',      
    right_on='Cod_Cliente', 
    how = 'left'
)


#print(df_u_indirecta_completa_socios)
#print("¿Hay coincidencias?")
#print(df_u_indirecta_completa[df_u_indirecta_completa['Cod_vend Z1'].notna()].head(10))

df_u_directa_completa_Socios = df_u_directa_completa_Socios.drop_duplicates(subset = 'Cód. Cliente', keep = 'first' )

#print(df_u_directa_completa_Socios['Cod_vend Z1'].dtype)
#print(df_u_directa_completa_Socios.columns)


df_u_directa_completa_Socios = Aplicar_Regla_Negocio_Z1_ZA(df_u_directa_completa_Socios)

df_u_directa_completa_Socios = Aplicar_regla_Negocio_Socio(df_u_directa_completa_Socios)

df_si_socios = df_u_directa_completa_Socios[df_u_directa_completa_Socios['Col_Socio'] == 'SI'].copy()
df_no_socios = df_u_directa_completa_Socios[df_u_directa_completa_Socios['Col_Socio'] == 'NO'].copy()

df_no_socios = df_no_socios.drop_duplicates(subset = 'Cód. Cliente', keep='first' )

df_u_directa_completa_Socios = pd.concat([df_si_socios, df_no_socios])

print(df_u_directa_completa_Socios)