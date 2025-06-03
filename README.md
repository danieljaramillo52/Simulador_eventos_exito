## Simulador de Descuentos Éxito

Proyecto desarrollado para Comercial Nutresa. Permite calcular los valores de descuentos para productos, así como su proyección de crecimiento en ventas (en pesos y unidades), a partir de parámetros ingresados por el usuario y archivos de insumo con información histórica de ventas y precios de los materiales.

---

## Insumos necesarios para la automatización

### Base de Precios

Archivo que contiene la lista de precios de los materiales seleccionables para la automatización.

- **Tipo/Formato:** Archivo Excel dinámico (sin macros)  
- **Nombre actual del archivo:** `Precios.xlsx`  
- **Columnas requeridas:**
  - PLU
  - SUBLINEA
  - P. LISTA
  - P. SUGERIDO  
- **Ubicación recomendada:**  
  `Simulador_eventos_exito\Insumos\Precios.xlsx`

---

### Base de Ventas

Archivo que contiene los registros de ventas de los materiales, tanto en pesos como en unidades.

- **Tipo/Formato:** Archivo Excel dinámico (sin macros)  
- **Nombre actual del archivo:** `base_vtas.xlsx`  
- **Columnas requeridas:**
  - Agrupación Formatos
  - Marca
  - Cod. SAP Unificado
  - PLU
  - EAN Unificado
  - Fabricante
  - Categoría
  - Subcategoría
  - Producto Unificado  
- **Ubicación recomendada:**  
  `Simulador_eventos_exito\Insumos\base_vtas.xlsx`

---

### Consideraciones

1. Se debe respetar la estructura actual de los archivos, con los encabezados ubicados directamente en la primera fila, y con los nombres de columna especificados anteriormente.  
   Aunque la interfaz permite seleccionar la ubicación de los archivos, se recomienda guardarlos en la carpeta asignada:  
   `Simulador_eventos_exito\Insumos`

2. Se sugiere mantener los nombres de archivo proporcionados para establecer un estándar de uso. No obstante, esto es opcional si se cumple correctamente el punto anterior.

3. Los archivos `base_vtas.xlsx` y `Precios.xlsx` se integran para formar la fuente de información principal, por lo que **ambos son indispensables para la ejecución correcta del proceso**.

---

## Archivo de Configuración (`config.yml`)

- **Tipo de archivo:** Archivo de parámetros YAML (`.yml`)
- **Propósito:** Controlar el funcionamiento interno de la aplicación mediante parametrización estructurada.

---

## Visualización del archivo editable (`editable.yml`)

Este archivo contiene configuraciones editables por el usuario para conceptos y herramientas, y se modifica según necesidad. A continuación se describe el procedimiento para editarlo.

### Edición de conceptos y herramientas ("Instructivo")

1. Abrimos el archivo **`editable.yaml`**

   - Buscar la aplicación **Notepad++** (previamente instalada) en el menú de inicio de Windows.

   ![Notepadd](Img/Notepad++.png)

2. En la barra superior, ir a **Archivo / File**, y luego seleccionar **Abrir / Open**.

   ![Abrir_archivo_notepadd](Img/Abrir_archivo_notepadd.png)

3. Navegar a la carpeta del proyecto `Simulador_eventos_exito` y seleccionar el archivo `editable.yaml`.

   ![editable_yaml](Img/editable_yaml.png)

4. Se abrirá una ventana con los conceptos y herramientas actualmente definidos.

   ![Modificaciones editable 1](Img/herramientas_conceptos.png)

5. Para eliminar un concepto o herramienta, simplemente borra la línea correspondiente.

   ![Modificaciones editable 1](Img/Modificaciones_editable.png)

6. Para agregar uno nuevo, posicionarse al final de la lista correspondiente (concepto o herramienta) y escribir el nuevo ítem con un guion `-` seguido del nombre.

   ![Modificaciones editable 1](Img/Modificaciones_editable-1.png)

   
   ![Modificaciones editable 2](Img/Modificaciones_editable-2.png)

Una vez realizadas las modificaciones, guardar los cambios haciendo clic en el ícono de guardar (parte superior).

   ![Modificaciones editable 3](Img/Modificaciones_editable-3.png)

⚠️ Este archivo solo debe editarse si se desea agregar o eliminar herramientas o conceptos. Si no es necesario, puede dejarse sin cambios.


## Responsables
### Provededor - XpertGroup.
* Daniel jaramillo Bustamante - daniel.jaramillo@xpertgroup.co

### Receptor - Comercial Nutresa.
* **Aréa TI:**
    * Sebastián Caro Aguirre scaro@comercialnutresa.com.co

