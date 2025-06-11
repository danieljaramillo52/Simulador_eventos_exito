import pandas as pd
import os
import numpy as np
import streamlit as st
from loguru import logger
from typing import List, Union, Literal
import yaml
import requests
from io import BytesIO
from datetime import date
import re
from PIL import Image


def procesar_configuracion(nom_archivo_configuracion: str) -> dict:
    """Lee un archivo YAML de configuración para un proyecto.

    Args:
        nom_archivo_configuracion (str): Nombre del archivo YAML que contiene
            la configuración del proyecto.

    Returns:
        dict: Un diccionario con la información de configuración leída del archivo YAML.
    """
    try:
        with open(nom_archivo_configuracion, "r", encoding="utf-8") as archivo:
            configuracion_yaml = yaml.safe_load(archivo)
        logger.success("Proceso de obtención de configuración satisfactorio")
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}")
        raise e

    return configuracion_yaml


def lectura_simple_excel(
    dir_insumo: str, nom_insumo: str, nom_hoja: str = None
) -> pd.DataFrame:
    """
    Lee un archivo de Excel y devuelve su contenido en un DataFrame.

    Args:
        dir_insumo (str): Ruta del directorio donde se encuentra el archivo.
        nom_insumo (str): Nombre del archivo de Excel (incluyendo la extensión).
        nom_hoja (str): Nombre de la hoja a leer dentro del archivo de Excel.

    Returns:
        pd.DataFrame: Contenido de la hoja de Excel como un DataFrame.

    Raises:
        Exception: Si ocurre algún error durante la lectura del archivo.
    """

    try:
        logger.info(f"Inicio lectura simple de {nom_insumo}")
        base_leida = pd.read_excel(
            dir_insumo + nom_insumo,
            sheet_name=nom_hoja,
            dtype=str,
        )
        logger.success(f"Lectura simple de {nom_insumo} realizada con éxito")
        return base_leida
    except Exception as e:
        logger.error(f"Proceso de lectura fallido: {e}")
        raise Exception(f"Error al leer el archivo: {e}")


def crear_boton_exportar(df, filename="selecciones.xlsx", key=None):
    """
    Crea un botón interactivo en Streamlit para exportar un DataFrame como archivo Excel descargable.

    Esta función genera un botón de descarga que permite al usuario exportar los datos contenidos
    en un DataFrame de pandas directamente desde la interfaz de Streamlit. El archivo se genera
    en memoria sin necesidad de almacenamiento temporal en disco.

    Args:
        df (pd.DataFrame): DataFrame de pandas que contiene los datos a exportar.
        filename (str, opcional): Nombre del archivo a descargar. Debe incluir extensión .xlsx.
                                  Por defecto: "selecciones.xlsx".
        key (str, opcional): Clave única para identificación del elemento en Streamlit. Si no se
                            proporciona, se generará automáticamente basado en el nombre de archivo.
                            Necesario para evitar conflictos cuando existen múltiples botones.

    Returns:
        None: La función no retorna ningún valor, pero renderiza un elemento interactivo en la UI.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'columna': [1, 2, 3]})
        >>> crear_boton_exportar(df, filename="datos.xlsx", key="boton_unic0")

        >>> # Uso con key automático
        >>> crear_boton_exportar(df, filename="reporte_diario.xlsx")

    Note:
        - Para prevenir errores de claves duplicadas en Streamlit, especialmente cuando se usan
        múltiples instancias del botón, es recomendable proveer una clave única mediante el parámetro `key`.
        - El archivo se genera usando openpyxl como motor de Excel, asegurando compatibilidad con
        formatos .xlsx modernos.
        - La función utiliza un buffer en memoria para máxima eficiencia, evitando operaciones de I/O en disco.
    """
    # Crear un buffer en memoria para almacenar el archivo Excel
    output = BytesIO()

    # Guardar el DataFrame en el buffer como un archivo Excel
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")

    # Obtener el contenido del buffer
    excel_data = output.getvalue()

    # Si no se proporciona un key, generar uno basado en el nombre del archivo
    key = key if key is not None else f"download_button_{filename}"

    # Botón de descarga con clave única
    st.download_button(
        label=f"Descargar {filename}",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=key,  # Clave única para evitar conflictos
    )


def eliminar_espacios_cols(df, columnas: str | list):
    """
    Elimina todos los espacios en blanco de los valores en las columnas
    especificadas de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame que contiene las columnas a limpiar.
        columnas (str o list): Nombre de la columna o lista de nombres de
                            columnas en las que se eliminarán los espacios
                            en blanco.

    Returns:
        pd.DataFrame: El DataFrame con los espacios en blanco eliminados de las columnas
                    especificadas.
    """
    # Si columnas es un solo nombre, convertirlo a lista
    if isinstance(columnas, str):
        columnas = [columnas]
    # Aplicar str.strip() solo a las columnas especificadas
    for columna in columnas:
        if columna in df.columns and df[columna].dtype == "object":
            df.loc[:, columna] = df[columna].str.replace(" ", "")
        else:
            print(f"La columna '{columna}' no existe o no es de tipo string.")
    return df


def concatenar_columnas_pd(
    dataframe: pd.DataFrame,
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
        #if not isinstance(dataframe, pd.DataFrame):
        #    raise TypeError("El argumento 'dataframe' debe ser un DataFrame de pandas.")

        # Verificar si las columnas especificadas existen en el DataFrame
        for col in cols_elegidas:
            if col not in dataframe.columns:
                raise KeyError(f"La columna '{col}' no existe en el DataFrame.")

        df_copy = dataframe.copy()

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
        return None  # 🔹 Retorna None en caso de error


# Cargar el archivo CSS
def load_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Archivo CSS no encontrado: {file_name}")
    except Exception as e:
        st.error(f"Error al cargar el CSS: {e}")


import base64
from io import BytesIO


def image_to_base64(image):
    """Convierte una imagen PIL a base64 para HTML inline"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def setup_ui():
    load_css("static/styles.css")  # Si tienes estilos base

    # Cargar imagen como base64 para incrustarla en HTML
    image_path = "Img/EXITO.png"
    image = Image.open(image_path).resize((100, 100))
    img_base64 = image_to_base64(image)

    # Usar una tabla HTML para alinear horizontalmente texto e imagen
    st.markdown(
        f"""
        <div style="background-color: #e8f8f5; padding: 10px 20px; border-radius: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="text-align: left;">
                        <h1 style="margin: 0; font-size: 2.5em; color: ##9bb80b;">
                            Cálculo descuentos éxito
                        </h1>
                    </td>
                    <td style="text-align: right; vertical-align: middle;">
                        <img src="data:image/png;base64,{img_base64}" alt="Logo Éxito" width="100">
                    </td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


# wrapper: Decorador (st.cache data.)
# Permite almacenar el resultado del método en cache.
# Así evitamos multiples llamadas a la API y consultas a los archivos en google shets.
@st.cache_data
def fetch_data_from_url(url: str | None) -> pd.DataFrame:
    """
    Obtiene datos JSON desde una URL y los convierte en un DataFrame de pandas.

    Args:
        url (str): La URL desde donde se obtendrán los datos JSON.

    Returns:
        JSON: Un elemento JSON con los datos obtenidos

    ¿Qué hace requests.get(url)?
        Realiza una solicitud HTTP GET:
            - Una solicitud GET es un tipo de solicitud HTTP que se utiliza para obtener datos de un servidor.

            - Cuando llamas a requests.get(url), se envía una solicitud GET a la URL proporcionada.

        Recibe una respuesta:
         El servidor procesa la solicitud y devuelve una respuesta. Esta respuesta incluye:
            - Un código de estado HTTP (por ejemplo, 200 para éxito, 404 para no encontrado, 500 para error del servidor, etc.).

            - Encabezados (metadata sobre la respuesta).

            - Cuerpo (los datos devueltos, como HTML, JSON, XML, etc.).

        Devuelve un objeto Response:
            - requests.get(url) devuelve un objeto de tipo Response, que contiene toda la información de la respuesta.

            - Puedes acceder a los datos de la respuesta usando los atributos y métodos de este objeto.
    """

    with requests.get(url) as response:
        if response.status_code == 200:
            data = response.json()
            return data  # Convertir JSON a DataFrame
        else:
            raise Exception(f"Error al obtener datos: {response.status_code}")


def lectura_auxiliares_css_js(nom_modulo: str, encoding: str = "utf-8"):
    """Procesa los archivos auxiliares tipo .css y .js para la modificación de estilos de la interfaz.

    Args:
        nom_modulo (str): Nombre del módulo dentro de la carpeta "static".
        encoding (str, optional): Codificación al abrir el archivo correspondiente. Defaults to "utf-8".

    Exceptions:
        FileNotFoundError: Si el archivo no existe en la ruta especificada.
        UnicodeDecodeError: Si hay un problema con la codificación del archivo.
        Exception: Captura cualquier otro error inesperado.
    """
    try:
        script_path = os.path.join("static", nom_modulo)

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"El archivo '{script_path}' no fue encontrado.")

        with open(script_path, "r", encoding=encoding) as f:
            script_content = f.read()

        st.markdown(f"<script>{script_content}</script>", unsafe_allow_html=True)

    except FileNotFoundError as e:
        st.error(f"Error: {e}")
    except UnicodeDecodeError:
        st.error(
            f"Error: No se pudo leer el archivo '{script_path}' debido a un problema de codificación."
        )
    except Exception as e:
        st.error(f"Error inesperado: {e}")


def json_a_dataframe(data):
    """
    Convierte una estructura de datos JSON en un DataFrame de pandas,
    usando la primera fila como los encabezados y estableciendo el tipo de datos a cadenas de texto (str).

    Parameters:
    data (list): Lista de listas donde la primera lista contiene los encabezados y el resto contiene los datos.

    Returns:
    DataFrame: Un DataFrame de pandas con los datos proporcionados, con las columnas establecidas
    según la primera fila y el tipo de datos de todas las columnas como cadenas de texto (str).

    Raises:
    ValueError: Si el JSON no tiene al menos dos filas (una para los encabezados y una para los datos).
    """
    try:
        if len(data) < 2:
            raise ValueError(
                "El JSON debe contener al menos dos filas: una para los encabezados y una para los datos."
            )

        df = pd.DataFrame(data[1:], columns=data[0], dtype=str)
        return df

    except ValueError as ve:
        logger.error(f"Error: {ve}")
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado: {e}")


def transformar_estructura(df: pd.DataFrame, columnas_referencia: list) -> pd.DataFrame:
    """
    Transforma un DataFrame de formato ancho a largo, manteniendo múltiples columnas de referencia.

    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con columnas de referencia y materiales separados.
    columnas_referencia : list
        Lista de columnas que deben mantenerse fijas.

    Retorna:
    --------
    pd.DataFrame
        DataFrame reestructurado con columnas de referencia y materiales en formato largo.
    """
    df_long = df.melt(
        id_vars=columnas_referencia, var_name="Material", value_name="Cantidad"
    )
    return df_long


def left_merge_on_columns(
    df1: pd.DataFrame, df2: pd.DataFrame, key_columns: list
) -> pd.DataFrame:
    """
    Realiza un left merge entre dos DataFrames usando una lista de columnas comunes como llave.

    Parámetros:
    -----------
    df1 : pd.DataFrame
        DataFrame base sobre el cual se hará el merge.
    df2 : pd.DataFrame
        DataFrame que se unirá a df1 basado en las columnas especificadas.
    key_columns : list
        Lista de nombres de columnas en las que se basará la fusión.

    Retorna:
    --------
    pd.DataFrame
        Un nuevo DataFrame con la combinación de df1 y df2, manteniendo todas las filas de df1.
    """
    # Validar que todas las columnas clave existen en ambos DataFrames
    for col in key_columns:
        if col not in df1.columns:
            raise KeyError(f"La columna '{col}' no está en df1")
        if col not in df2.columns:
            raise KeyError(f"La columna '{col}' no está en df2")

    # Realizar el left merge
    merged_df = df1.merge(df2, on=key_columns, how="left")

    return merged_df


def actualizar_dias(df, dict_cols):
    """Actualiza los dias si las fechas fueron modificadas"""
    FECHA_FIN = "fecha_fin"
    FECHA_INICIO = "fecha_inicio"

    df[dict_cols["Dias de la actividad"]] = abs(
        pd.to_datetime(df[FECHA_FIN]) - pd.to_datetime(df[FECHA_INICIO])
    ).dt.days
    return df


def calcular_unidades(
    df,
    dict_cols,
):
    DIAS_MES = 30
    """
    Calcula las unidades de actividad en función del promedio mensual y los días.

    Args:
        df (pd.DataFrame): DataFrame de insumos.
        dict_cols (dict): Configuración con nombres de columnas y valores constantes.

    Returns:
        pd.DataFrame: DataFrame con columna 'Unidades' añadida.
    """
    df["Unidades"] = np.ceil(
        (df[dict_cols["Promedio Mes Und"]].astype(float) / DIAS_MES
    ) * df[dict_cols["Dias de la actividad"]].astype(float))
    return df


def calcular_totales(df, porcentaje_crecimiento):
    """
    Calcula el crecimiento y total de unidades.

    Args:
        df (pd.DataFrame): DataFrame con columna 'Unidades'.
        porcentaje_crecimiento (float): Porcentaje de crecimiento a aplicar.

    Returns:
        pd.DataFrame: DataFrame con columnas 'Crec actividad' y 'unidades_totales'.
    """
    df["Crec actividad"] = df["Unidades"] * porcentaje_crecimiento / 100
    df["unidades_totales"] = np.ceil(df["Unidades"] + df["Crec actividad"])
    
    df["Crec actividad"] = df["Crec actividad"].astype(int)
    return df


def calcular_venta(df, dict_cols):
    """
    Calcula la venta total de la actividad.

    Args:
        df (pd.DataFrame): DataFrame con columna 'unidades_totales'.
        dict_cols (dict): Configuración con nombres de columnas.

    Returns:
        pd.DataFrame: DataFrame con columna 'Venta de la actividad' añadida.
    """
    df["Venta de la actividad"] = df["unidades_totales"] * df[
        dict_cols["Precio de venta"]
    ].astype(float)
    
    df["Venta de la actividad"] = df["Venta de la actividad"].astype(int)
    
    return df


def obtener_rango_valido_desde_texto(
    texto: str, por_defecto: tuple[int, int] = (5, 10)
) -> tuple[int, int]:
    """
    Extrae un rango de dos números enteros desde un texto. Si no se encuentran dos números, retorna un rango por defecto.

    Args:
        texto (str): Texto que contiene números, por ejemplo "5% - 10%".
        por_defecto (tuple[int, int]): Rango de retorno si falla la extracción.

    Returns:
        tuple[int, int]: Rango de dos valores enteros.
    """
    try:
        numeros = tuple(map(int, re.findall(r"\d+", texto)))
        if len(numeros) < 2:
            return por_defecto
        return numeros
    except Exception:
        return por_defecto


def preparar_df_materiales(df):
    """
    Convierte y normaliza la lista de materiales a DataFrame.

    Args:
        df_materiales: Lista de materiales.
        dict_cols (dict): Diccionario de columnas relevantes.

    Returns:
        pd.DataFrame: DataFrame con columna 'rango' normalizada.
    """
    df["rango%"] = df["rango"].astype(int) / 100
    return df


def calcular_vtas_totales(df: pd.DataFrame, cols: list[str]):
    """Calcula un promedio simple sobre varias columnas de un dataframe

    Args:
        df: type (pd.Dataframe). Dataframe sobre le que se calculan los promedios.
        cols: type (list[str]). Columnas necesarias.

    Return:
        serie_prom: type (pd.Series). Serie con los promedios calculados."""

    sumas_totales = df[cols].sum().astype(int)
    return sumas_totales


def calcular_descuento(df):
    """
    Calcula el costo del descuento según el rango y venta.

    Args:
        df (pd.DataFrame): DataFrame con columnas necesarias.
        dict_cols (dict): Diccionario de columnas relevantes.

    Returns:
        pd.Series: Columna con valores del costo del descuento.
    """
    return (df["Venta de la actividad"] * df["rango%"]).round().astype(int)


def reemplazar_mes(df):
    DICT_MESES = {
        "January": "Enero",
        "February": "Febrero",
        "March": "Marzo",
        "April": "Abril",
        "May": "Mayo",
        "June": "Junio",
        "July": "Julio",
        "August": "Agosto",
        "September": "Septiembre",
        "October": "Octubre",
        "November": "Noviembre",
        "December": "Diciembre",
    }
    df["mes"] = df["mes"].map(DICT_MESES)
    return df

def procesar_insumo(df_insumo, porcentaje_crecimiento, dict_cols):
    """
    Ejecuta todo el flujo de procesamiento de insumos con crecimiento y descuentos.

    Args:
        df_insumo (pd.DataFrame): DataFrame de insumos original.
        porcentaje_crecimiento (float): Porcentaje de crecimiento para unidades.
        dict_cols (dict): Dict de columnas necesarias.

    Returns:
        pd.DataFrame: DataFrame procesado con todas las columnas calculadas.
    """
    df = df_insumo.copy()
    df = actualizar_dias(df, dict_cols)
    df = calcular_unidades(df, dict_cols)
    df = calcular_totales(df, porcentaje_crecimiento)
    df = calcular_venta(df, dict_cols)
    df = preparar_df_materiales(df)
    df = reemplazar_mes(df)
    df["Costo del descuento"] = calcular_descuento(df)
    return df


def aplanar_diccionario(diccionario: dict, clave_aplanar: str = "Fecha") -> dict:
    """
    Aplana un diccionario anidado moviendo las claves de un subdiccionario especificado al nivel superior.

    Parámetros:
        diccionario (dict): Diccionario original con posible anidación
        clave_aplanar (str): Clave del subdiccionario a aplanar (default: "Fecha")

    Retorno:
        dict: Diccionario aplanado con todas las claves al nivel superior

    Ejemplo:
        >>> dict_original = {"a": 1, "Fecha": {"mes": "Enero", "año": 2023}}
        >>> aplanar_diccionario(dict_original)
        {"a": 1, "mes": "Enero", "año": 2023}
    """
    return {
        **{k: v for k, v in diccionario.items() if k != clave_aplanar},
        **diccionario.get(clave_aplanar, {}),
    }


def renombrar_columnas_con_diccionario(
    df: pd.DataFrame, cols_to_rename: dict
) -> pd.DataFrame:
    """Funcion que toma un diccionario con keys ( nombres actuales ) y values (nuevos nombres) para remplazar nombres de columnas en un dataframe.
    Args:
        base: dataframe al cual se le harán los remplazos
        cols_to_rename: diccionario con nombres antiguos y nuevos
    Result:
        base_renombrada: Base con las columnas renombradas.
    """
    base_renombrada = None

    try:
        base_renombrada = df.rename(columns=cols_to_rename, inplace=False)
        # logger.success("Proceso de renombrar columnas satisfactorio: ")
    except Exception:
        logger.critical("Proceso de renombrar columnas fallido.")
        raise Exception

    return base_renombrada


def reemplazar_columna_en_funcion_de_otra(
    df: pd.DataFrame,
    nom_columna_a_reemplazar: str,
    nom_columna_de_referencia: str,
    mapeo: dict,
) -> pd.DataFrame:
    """
    Reemplaza los valores en una columna en función de los valores en otra columna en un DataFrame.

    Args:
        df (pandas.DataFrame): El DataFrame en el que se realizarán los reemplazos.
        columna_a_reemplazar (str): El nombre de la columna que se reemplazará.
        columna_de_referencia (str): El nombre de la columna que se utilizará como referencia para el reemplazo.
        mapeo (dict): Un diccionario que mapea los valores de la columna de referencia a los nuevos valores.

    Returns:
        pandas.DataFrame: El DataFrame actualizado con los valores reemplazados en la columna indicada.
    """
    try:
        # logger.info(
        #    f"Inicio de remplazamiento de datos en {nom_columna_a_reemplazar}"
        # )
        df.loc[:, nom_columna_a_reemplazar] = np.where(
            df[nom_columna_de_referencia].isin(mapeo.keys()),
            df[nom_columna_de_referencia].map(mapeo),
            df[nom_columna_a_reemplazar],
        )
        logger.success(
            f"Proceso de remplazamiento en {nom_columna_a_reemplazar} exitoso"
        )
    except Exception as e:
        logger.critical(
            f"Proceso de remplazamiento de datos en {nom_columna_a_reemplazar} fallido."
        )
        raise e

    return df


@staticmethod
def Seleccionar_columnas_pd(
    df: pd.DataFrame, cols_elegidas: List[str]
) -> pd.DataFrame | None:
    """
    Filtra y retorna las columnas especificadas del DataFrame.

    Parámetros:
    dataframe (pd.DataFrame): DataFrame del cual se filtrarán las columnas.
    cols_elegidas (list): Lista de nombres de las columnas a incluir en el DataFrame filtrado.

    Retorna:
    pd.DataFrame: DataFrame con las columnas filtradas.
    """
    try:
        # Verificar si dataframe es un DataFrame de pandas
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El argumento 'dataframe' debe ser un DataFrame de pandas.")

        # Filtrar las columnas especificadas
        df_filtrado = df[cols_elegidas]

        # Registrar el proceso
        logger.info(f"Columnas filtradas: {', '.join(cols_elegidas)}")

        return df_filtrado

    except KeyError as ke:
        error_message = (
            f"Error: Columnas especificadas no encontradas en el DataFrame: {str(ke)}"
        )
        return df
    except Exception as e:
        logger.critical(f"Error inesperado al filtrar columnas: {str(e)}")


def group_by_and_operate(
    df: pd.DataFrame,
    group_col: Union[str, List[str]],
    operation_cols: Union[str, List[str]],
    operation: Literal["sum", "mean", "count"] = "sum",
) -> Union[pd.DataFrame, None]:
    """
    Agrupa un DataFrame por una o varias columnas y aplica una operación sobre otras columnas.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame de entrada que contiene los datos a procesar.
    group_col : str or list of str
        Columna o lista de columnas por las que se agrupará el DataFrame.
    operation_cols : str or list of str
        Columna o columnas sobre las que se aplicará la operación (sum, mean, count).
    operation : {'sum', 'mean', 'count'}, default='sum'
        Operación a realizar sobre las columnas indicadas.

    Returns
    -------
    pd.DataFrame or None
        DataFrame resultante con los valores agrupados y operados, o `None` si ocurre un error.
    """
    try:
        group_keys = [group_col] if isinstance(group_col, str) else group_col
        target_cols = (
            [operation_cols] if isinstance(operation_cols, str) else operation_cols
        )

        if operation == "sum":
            result_df = df.groupby(group_keys)[target_cols].sum().reset_index()
        elif operation == "mean":
            result_df = df.groupby(group_keys)[target_cols].mean().reset_index()
        elif operation == "count":
            result_df = df.groupby(group_keys)[target_cols].count().reset_index()
        else:
            raise ValueError(f"Operación no soportada: '{operation}'")

        logger.info(f"Agrupación y operación '{operation}' realizadas con éxito.")
        return result_df

    except Exception as e:
        logger.critical(f"Error al realizar la operación '{operation}': {e}")
        return None


def filtrar_por_valores(
    df: pd.DataFrame, columna: str, valores: list[str | int], incluir: bool = True
) -> pd.DataFrame | None:
    """
    Filtra un DataFrame incluyendo o excluyendo filas según los valores en una columna.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame a filtrar.
    columna : str
        Nombre de la columna sobre la cual aplicar el filtro.
    valores : list of str or int
        Lista de valores a incluir o excluir.
    incluir : bool, default=True
        Si True, incluye las filas con los valores indicados. Si False, las excluye.

    Returns
    -------
    pd.DataFrame or None
        DataFrame filtrado o None si ocurre un error.
    """
    try:
        if isinstance(valores, (str, int)):
            valores = [valores]

        if incluir:
            df_filtrado = df[df[columna].isin(valores)]
        else:
            df_filtrado = df[~df[columna].isin(valores)]

        return df_filtrado

    except Exception as e:
        logger.critical(f"Error al filtrar por valores en la columna '{columna}': {e}")
        return None


def Cambiar_tipo_dato_multiples_columnas_pd(
    base: pd.DataFrame, list_columns: list, type_data: type
) -> pd.DataFrame:
    """
    Función que toma un DataFrame, una lista de sus columnas para hacer un cambio en el tipo de dato de las mismas.

    Args:
        base (pd.DataFrame): DataFrame que es la base del cambio.
        list_columns (list): Columnas a modificar su tipo de dato.
        type_data (type): Tipo de dato al que se cambiarán las columnas (ejemplo: str, int, float).

    Returns:
        pd.DataFrame: Copia del DataFrame con los cambios.
    """
    try:
        # Verificar que el DataFrame tenga las columnas especificadas
        for columna in list_columns:
            if columna not in base.columns:
                raise KeyError(f"La columna '{columna}' no existe en el DataFrame.")

        # Cambiar el tipo de dato de las columnas
        base_copy = (
            base.copy()
        )  # Crear una copia para evitar problemas de SettingWithCopyWarning
        base_copy[list_columns] = base_copy[list_columns].astype(type_data)

        return base_copy

    except Exception as e:
        logger.critical(f"Error en Cambiar_tipo_dato_multiples_columnas: {e}")


def formatear_fecha(fecha_dict):
    if not isinstance(fecha_dict, dict):
        return {}
    return {
        "fecha_inicio": (
            fecha_dict.get("fecha_inicio").strftime("%Y-%m-%d")
            if isinstance(fecha_dict.get("fecha_inicio"), date)
            else ""
        ),
        "fecha_fin": (
            fecha_dict.get("fecha_fin").strftime("%Y-%m-%d")
            if isinstance(fecha_dict.get("fecha_fin"), date)
            else ""
        ),
        "mes": fecha_dict.get("mes", ""),
    }
