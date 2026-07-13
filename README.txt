HERRAMIENTA DE AJUSTE POR INFLACION DEL ESTADO DE RESULTADOS
RT 6 + RT 54 FACPCE
================================================================

Que es esto
-----------
Un prototipo funcional (app web local) que permite:
 1. Subir el balance provisional que baja el cliente de su sistema contable.
 2. Cargar el indice FACPCE de cada mes del ejercicio.
 3. Elegir que cuentas se ajustan por inflacion y cuales no (se guarda por cliente).
 4. Generar y descargar el Estado de Resultados historico vs ajustado, cuenta por cuenta.

Como correrla en tu computadora
--------------------------------
1. Necesitas tener Python instalado (3.9 o superior).
2. Abri una terminal en esta carpeta.
3. Instala las dependencias (una sola vez):

       pip install -r requirements.txt

4. Arranca la aplicacion:

       streamlit run app.py

5. Se va a abrir sola en el navegador (http://localhost:8501). Si no se abre sola,
   copia esa direccion en el navegador.

Como se usa
-----------
1. Elegi un cliente existente o creá uno nuevo (con su nombre).
2. Subí el Excel del balance (el mismo formato que bajaste del sistema).
3. Completá el índice FACPCE de cada mes detectado.
4. Revisá las cuentas: por defecto vienen todas tildadas como "ajustable".
   Destildá las que correspondan a partidas ya expresadas en moneda de cierre
   (resultados financieros, diferencias de cambio, RECPAM, etc.).
5. Apretá "Calcular ajuste por inflacion".
6. Descargá el Excel con el resultado.

Actualizaciones futuras
------------------------
Si el mes que viene el cliente vuelve a bajar el archivo (o lo corrige), subí
el nuevo Excel eligiendo el mismo cliente: la seleccion de cuentas ajustables
que ya guardaste se recupera sola. Solo hay que revisar si aparecieron cuentas
nuevas (quedan marcadas como ajustables por defecto, para que las repases).

Que falta para que la use el cliente final (sin instalar nada)
----------------------------------------------------------------
Este prototipo corre en tu computadora. El siguiente paso, cuando la logica de
calculo te cierre del todo, es publicarla en un link (hosting) para que el
cliente la use sin instalar Python. Lo charlamos cuando llegue el momento.

Estructura de archivos
-----------------------
 app.py                -> interfaz (Streamlit)
 balance_parser.py      -> lee y entiende el Excel del sistema contable
 inflation_engine.py    -> calcula el ajuste por inflacion
 excel_export.py        -> genera el Excel de salida
 storage.py              -> guarda la configuracion de cuentas por cliente
 data/clientes/          -> ahi se guardan los archivos de configuracion (uno por cliente)
