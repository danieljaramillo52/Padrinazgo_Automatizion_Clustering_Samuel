Grupo Nutresa.

Areas atendidas por XpertGroup.

1. Comercial Nutresa (Nosotros)
2. **Servicios Nutresa** (Erwing y Juan Jose).
3. Novaventa. (Maquinas expendedoras.) 

Servicios (Parte técnologica del grupo nutresa). Todos dependen de la infrastructura de servicos nutresa. Y dependen de los permisos. 

Comercial Nutresa: Parte comercial: (Productos Secos. ) => NO son Carnicos Secos/ Helados NO.

Comercial Nutresa : (Principalmente Logistica)
- Trade de Marcas (Manejo de Activos)
- Ppto y Nomina (Financiera)
- Servicios. (Aplicativo Pideky)

Ppto y Nomina: Nomina variable (Funcional y exitoso) / Variable logistica (Funcial) / Nomina parte 1 => Especialista de CN de nómina. 

Financiera _ Ppto : **CxS**: **Ppto de toda la compañia (CN)** 

Cxs parte 1: Ppto (Predefinido de vtas / dctos / gastos etc.) y Real: (vtas / dctos y gastos reales):  2 bases (Tablas Ppto y Real.) 

Resultado acumula a lo largo del año: Local / 10 millones de registros.

- SQllite3.
- PostgreSQl (Actualmente).

CXS parte 2: Toma otros archivos , y hace una distribución base vtas a todo nivel utulizando además el resultado (PostgreSQl - cxs 1). a otro PostgreSQL.

CxS parte 3: Tambien con PostgrSQL.

Automatización en 3 parte. CXS impacta a todas las areas de la compañia. Todo el mundo esta esperand el informe que el especialista de CXS va a generar con las automatizaciones que yo hice. 

CECOS (CUBOS) != Secos (prodcutos secos)

Utilidad directa. 
5-10 personas.

---
Semaforo de activos. (Activos comerciales: Herramientas que CN le da , le provee a sus clientes como estrategia para la venta. ) Muebles snakeros / Nueveras.


Driver en el contexto CN: (Se trata de un archivo auxiliar (.xlsx) que sirve para homologar / completar / sustituir / arreglar infomación. )


Modelos de atención.

Directa: Venta directa - Relacionado con person al contratado en nomina de CN (Jefes de venta y vendedores) : 20000 Y 30000 Clientes. Son los clientes mas importnates de CN y lo clientes más grnades. (Por unidad.)

Universo directa => 0 - 25000 registros.
Maestra directa

Algo clave : Siempre va a exsitir un código: Llamese (Codigo de cliente  / codigo sap  / codigo crm ) Es el codgio que maneja al cliente. 

Indirecta:  Relacionado con 63 Agentes comerciales:
    
    **Agente Comercial**: Es una empresa que actua como intermediario para maximizar el volumen de vtas de CN. ¿Por qué existen? Por que la atención directa es cara , implica nomina y en parte por temas de acceso.  (sistema información de la directa : SAP)

    CN vende Agente Comercial -> Cod ac / r_id_agente. Agente comercial revende (distribuye a todos pequeños de su región  de su atención etc. ) , clientes de la indirecta en medellin en lugares conocidos. 

    Cliente: Cod Cliente / r_id_cliente / codigo ecom (sistema de información diferente al de la directa ).

    Generalmente un **cliente lo atiende  varios agentes**, un agente atiende muchos clientes.  La combinacion de la clave 
    
    (COD AC + COD CLI) es única.  "Verdadero Codigo del cliente de la indirecta"

200000 a 230000 clientes. (Eso implica que los archivos de indirecta son mucho mas grandes 3000000 registros).


