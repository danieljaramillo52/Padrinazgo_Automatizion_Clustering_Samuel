import pandas as pd 

df_u_directa = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo Directa.xlsm",
                             sheet_name = "Maestra")
#print(df_u_directa)
#print("----------------------------")   #Revicioón de tabla completa
print(df_u_directa.columns)

df_u_directa = df_u_directa.iloc[:, list(range(7)) + [22]]

#print(df_u_directa)
#print("----------------------------")
#print(df_u_directa.columns)

df_u_indirecta = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\Universo Indirecta.xlsm")

print(df_u_indirecta)

df_Bas_Socio = pd.read_excel(r"C:\Users\samuel.molina\Padrinazgo_Automatizion_Clustering_Samuel\Insumos\BaseSocios.xlsm")

#print(df_Bas_Socio.columns)