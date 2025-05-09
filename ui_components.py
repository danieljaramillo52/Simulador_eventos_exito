from datetime import datetime
from io import BytesIO
import streamlit as st
import st_file_uploader as stf
import pandas as pd
from datetime import datetime
from typing import Any, Optional, Tuple, List, Union

def add_key_session_state(clave: str, valor_inicial: Any) -> None:
    """
    Inicializa una clave en st.session_state con un valor por defecto si no existe.

    Args:
        clave (str): Nombre de la variable a inicializar en session_state.
        valor_inicial (Any): Valor por defecto que se asignará si la clave no existe.

    Returns:
        None

    Raises:
        TypeError: Si 'clave' no es una cadena de texto.
        RuntimeError: Si st.session_state no está disponible en el entorno actual.
    """
    try:
        if not isinstance(clave, str):
            raise TypeError("La clave debe ser de tipo str.")

        if not hasattr(st, "session_state"):
            raise RuntimeError("st.session_state no está disponible.")

        if clave not in st.session_state:
            st.session_state[clave] = valor_inicial

    except Exception as e:
        st.error(f"Error al inicializar '{clave}': {e}")


def set_key_session_state(clave: str, valor: Any) -> None:
    """
    Asigna o actualiza un valor en st.session_state.

    Args:
        clave (str): Nombre de la variable en session_state.
        valor (Any): Valor que se asignará.
    """
    if not isinstance(clave, str):
        raise TypeError("La clave debe ser de tipo str.")
    st.session_state[clave] = valor


class TextInputManager:
    """
    Maneja una caja de texto en Streamlit con validación numérica,
    advertencias y ubicación configurable.
    """

    def __init__(
        self,
        clave: str,
        etiqueta: str,
        valor_por_defecto: str = "",
        usar_sidebar: bool = True,
        tipo: int | float = float,
        minimo: Optional[float] = None,
        maximo: Optional[float] = None,
        mensaje_error: Optional[str] = None,
    ):
        """
        Inicializa el gestor del campo de texto.

        Args:
            clave (str): Clave única para session_state y key del widget.
            etiqueta (str): Etiqueta visible junto a la caja de texto.
            valor_por_defecto (str): Texto inicial en la caja.
            usar_sidebar (bool): Si True, se muestra en el sidebar; de lo contrario, en el cuerpo principal.
            tipo (type): Tipo numérico esperado (int o float).
            minimo (float): Valor mínimo permitido.
            maximo (float): Valor máximo permitido.
            mensaje_error (str): Mensaje personalizado para mostrar si hay error.
        """
        self.clave = clave
        self.etiqueta = etiqueta
        self.usar_sidebar = usar_sidebar
        self.valor_por_defecto = valor_por_defecto
        self.tipo = tipo
        self.minimo = minimo
        self.maximo = maximo
        self.mensaje_error = (
            mensaje_error or f"Ingrese un número válido entre {minimo} y {maximo}."
        )

        self._show_input()

    def _show_input(self):
        input_func = st.sidebar.text_input if self.usar_sidebar else st.text_input

        valor_ingresado = input_func(
            label=self.etiqueta, value=self.valor_por_defecto, key=self.clave
        )

        st.session_state[f"{self.clave}_valido"] = False

        if self.tipo == str:
            if valor_ingresado.strip():
                st.session_state[f"{self.clave}_valido"] = True
            else:
                st.warning("Este campo no puede estar vacío.")
        else:
            try:
                valor_numerico = self.tipo(valor_ingresado)

                if (self.minimo is not None and valor_numerico < self.minimo) or (
                    self.maximo is not None and valor_numerico > self.maximo
                ):
                    st.warning(self.mensaje_error)
                else:
                    st.session_state[f"{self.clave}_valido"] = True
            except ValueError:
                if valor_ingresado.strip():
                    st.warning("Debe ingresar un número válido.")

    def get_value(self) -> Optional[Union[int, float, str]]:
        """
        Retorna el valor ingresado si es válido, convertido según el tipo especificado.

        Returns:
            int, float, str o None
        """
        if not st.session_state.get(f"{self.clave}_valido", False):
            return None

        try:
            return (
                self.tipo(st.session_state[self.clave])
                if self.tipo != str
                else st.session_state[self.clave]
            )
        except:
            return None

    def is_valid(self) -> bool:
        """
        Indica si el valor ingresado es numérico y está dentro del rango.

        Returns:
            bool
        """
        return st.session_state.get(f"{self.clave}_valido", False)

    def reset(self) -> None:
        """
        Marca el text_input para reiniciarse en la próxima ejecución.

        Nota: No modifica session_state directamente si el widget ya fue instanciado.
        """
        st.session_state[f"{self.clave}_reset"] = True


class FileUploaderManager:
    """
    Maneja un cargador de archivos personalizado usando st_file_uploader,
    con persistencia en session_state y ubicación configurable. Soporta múltiples archivos.
    """

    def __init__(
        self,
        clave: str,
        titulo: str,
        uploader_msg: str,
        limit_msg: str,
        button_msg: str,
        tipo_archivos: Optional[List[str]] = None,
        icon: str = "MdFileUpload",
        usar_sidebar: bool = False,
        use_cols: Optional[List[str]] = None,
    ):
        self.clave = clave
        self.tipo_archivos = tipo_archivos
        self.usar_sidebar = usar_sidebar
        self.titulo = titulo
        self.use_cols = use_cols

        self.uploader = stf.create_custom_uploader(
            uploader_msg=uploader_msg,
            limit_msg=limit_msg,
            button_msg=button_msg,
            icon=icon,
        )

        self.archivos = self._mostrar_uploader()

    def _mostrar_uploader(self) -> List[st.runtime.uploaded_file_manager.UploadedFile]:
        if self.usar_sidebar:
            with st.sidebar:
                st.markdown(f"### {self.titulo}")
                archivos = self.uploader.file_uploader(
                    label="",
                    type=self.tipo_archivos,
                    accept_multiple_files=True,
                    key=self.clave,
                )
        else:
            st.markdown(f"### {self.titulo}")
            archivos = self.uploader.file_uploader(
                label="",
                type=self.tipo_archivos,
                accept_multiple_files=True,
                key=self.clave,
            )

        if archivos:
            for archivo in archivos:
                st.success(
                    f"✅ Archivo cargado: {getattr(archivo, 'name', 'desconocido')}"
                )
        return archivos or []

    def get_archivos(self) -> List[st.runtime.uploaded_file_manager.UploadedFile]:
        return self.archivos

    def uploaded_files(self) -> bool:
        return bool(self.archivos)

    def leer_archivos(self) -> List[pd.DataFrame]:
        """
        Lee los archivos cargados como DataFrames si son .csv o .xlsx.

        Returns:
            List[pd.DataFrame]
        """
        dataframes = []
        for archivo in self.archivos:
            try:
                nombre = getattr(archivo, "name", None)
                if nombre is None:
                    raise ValueError("Archivo sin nombre válido")

                if isinstance(archivo, bytes):
                    buffer = BytesIO(archivo)
                else:
                    buffer = BytesIO(archivo.read())

                if nombre.endswith(".csv"):
                    df = pd.read_csv(buffer)
                elif nombre.endswith(".xlsx"):
                    df = pd.read_excel(
                        buffer, dtype=str, engine="openpyxl", usecols=self.use_cols
                    )
                else:
                    continue

                dataframes.append(df)
            except Exception as e:
                nombre = getattr(archivo, "name", "Archivo desconocido")
                st.error(f"❌ Error leyendo {nombre}: {e}")
        return dataframes

    def reset(self) -> None:
        st.session_state[f"{self.clave}_reset"] = True


class SelectBoxManager:
    """
    Maneja un selectbox en Streamlit con soporte para placeholder,
    persistencia en session_state, validación, y reinicio controlado.
    """

    SELECCION_INVALIDA = "Seleccione una opción..."

    def __init__(
        self,
        clave: str,
        etiqueta: str,
        opciones: List[str],
        placeholder: str = SELECCION_INVALIDA,
        usar_sidebar: bool = True,
    ):
        """
        Inicializa el gestor del selectbox.

        Args:
            clave (str): Clave única para session_state y key del widget.
            etiqueta (str): Texto que se muestra sobre el selectbox.
            opciones (List[str]): Lista de opciones válidas.
            placeholder (str): Valor por defecto no seleccionable.
            usar_sidebar (bool): Si True, se muestra en la barra lateral; de lo contrario, en el cuerpo principal.
        """
        if not opciones or not all(isinstance(op, str) for op in opciones):
            raise ValueError("Las opciones deben ser una lista de strings no vacía.")

        self.clave = clave
        self.etiqueta = etiqueta
        self.opciones = opciones
        self.placeholder = placeholder
        self.usar_sidebar = usar_sidebar

        self._show_selectbox()

    def _show_selectbox(self):
        opciones_mostradas = [self.placeholder] + self.opciones

        # Si se solicitó un reset previamente, aplicar ahora
        if st.session_state.get(f"{self.clave}_reset", False):
            st.session_state[self.clave] = self.placeholder
            st.session_state[f"{self.clave}_reset"] = False

        # Inicializa si aún no existe
        if self.clave not in st.session_state:
            st.session_state[self.clave] = self.placeholder

        # Mostrar el selectbox con una clave explícita
        if self.usar_sidebar:
            st.sidebar.selectbox(
                label=self.etiqueta,
                options=opciones_mostradas,
                index=opciones_mostradas.index(st.session_state[self.clave]),
                key=self.clave,
            )
        else:
            st.selectbox(
                label=self.etiqueta,
                options=opciones_mostradas,
                index=opciones_mostradas.index(st.session_state[self.clave]),
                key=self.clave,
            )

        # Guarda internamente el valor actual
        self.clave_actual_menu = st.session_state[self.clave]

    def get(self) -> str:
        """Devuelve la opción actualmente seleccionada."""
        return st.session_state.get(self.clave, self.clave_actual_menu)

    def is_valid(self) -> bool:
        """Indica si la selección es válida (distinta del placeholder)."""
        return st.session_state.get(self.clave) in self.opciones

    def reset(self) -> None:
        """
        Marca el selectbox para reiniciarse al placeholder en la próxima ejecución.

        Nota: No modifica session_state directamente si el widget ya fue instanciado.
        """
        st.session_state[f"{self.clave}_reset"] = True


class SliderManager:
    """
    Maneja un slider en Streamlit con soporte para persistencia en session_state,
    ubicación en el sidebar o en el cuerpo principal, y validación de rango.
    """

    def __init__(
        self,
        clave: str,
        etiqueta: str,
        rango: Tuple[int, int],
        valor_inicial: Optional[int] = None,
        usar_sidebar: bool = True,
        paso: int = 1,
    ):
        """
        Inicializa el gestor del slider.

        Args:
            clave (str): Clave para session_state.
            etiqueta (str): Texto que se muestra sobre el slider.
            rango (Tuple[int, int]): Rango mínimo y máximo permitido.
            valor_inicial (int, opcional): Valor inicial del slider. Si no se da, se toma el mínimo.
            usar_sidebar (bool): Si True, se muestra en la barra lateral.
            paso (int): Incremento entre valores del slider.
        """
        if not isinstance(rango, tuple) or len(rango) != 2:
            raise ValueError("El rango debe ser una tupla de dos enteros (min, max).")
        if rango[0] >= rango[1]:
            raise ValueError("El valor mínimo del rango debe ser menor que el máximo.")

        self.clave = clave
        self.etiqueta = etiqueta
        self.rango = rango
        self.valor_inicial = valor_inicial if valor_inicial is not None else rango[0]
        self.usar_sidebar = usar_sidebar
        self.paso = paso

        self._mostrar_slider()

    def _mostrar_slider(self):
        if self.clave not in st.session_state:
            st.session_state[self.clave] = self.valor_inicial

        if self.usar_sidebar:
            valor = st.sidebar.slider(
                label=self.etiqueta,
                min_value=self.rango[0],
                max_value=self.rango[1],
                value=st.session_state[self.clave],
                step=self.paso,
            )
        else:
            valor = st.slider(
                self.etiqueta,
                min_value=self.rango[0],
                max_value=self.rango[1],
                value=st.session_state[self.clave],
                step=self.paso,
            )

        st.session_state[self.clave] = valor

    def get(self) -> int:
        """Devuelve el valor actual del slider."""
        return st.session_state[self.clave]

    def is_valid(self) -> bool:
        """Valida si el valor actual está dentro del rango definido."""
        valor = st.session_state[self.clave]
        return self.rango[0] <= valor <= self.rango[1]

    def reset(self) -> None:
        """Reinicia el slider a su valor inicial."""
        st.session_state[self.clave] = self.valor_inicial


class ButtonTracker:
    """
    Gestiona el estado persistente de un botón en Streamlit usando session_state.

    Esta clase permite manejar si un botón ha sido presionado durante la sesión,
    sin entrar en conflicto con las restricciones de Streamlit respecto al uso de claves.
    """

    def __init__(
        self, clave: str, etiqueta: str = "Enviar", usar_sidebar: bool = False
    ):
        """
        Inicializa el botón y su estado asociado en session_state.

        Args:
            clave (str): Identificador lógico único del botón para el seguimiento de su estado.
            etiqueta (str): Texto visible que se muestra en el botón.
            usar_sidebar (bool): Si es True, el botón se renderiza en la barra lateral;
                                 en caso contrario, en el cuerpo principal.
        """
        self.clave_estado = (
            f"{clave}_estado"  # Clave para el estado del botón (presionado o no)
        )
        self.clave_widget = f"{clave}_widget"  # Clave para el widget visual del botón
        self.etiqueta = etiqueta
        self.usar_sidebar = usar_sidebar
        self._inicializar_estado()
        self._renderizar_boton()

    def _inicializar_estado(self):
        """
        Inicializa la clave de estado en session_state si aún no existe.

        Este valor es usado para determinar si el botón fue presionado.
        """
        if self.clave_estado not in st.session_state:
            st.session_state[self.clave_estado] = False

    def _renderizar_boton(self):
        """
        Renderiza el botón en la ubicación especificada.

        Si el botón es presionado por el usuario, actualiza su estado lógico
        en session_state a True para permitir su consulta posterior.
        """
        presionado = (
            st.sidebar.button(label=self.etiqueta, key=self.clave_widget)
            if self.usar_sidebar
            else st.button(label=self.etiqueta, key=self.clave_widget)
        )
        if presionado:
            st.session_state[self.clave_estado] = True

    def fue_presionado(self) -> bool:
        """
        Verifica si el botón fue presionado en algún momento durante la sesión.

        Returns:
            bool: True si el botón fue presionado, False en caso contrario.
        """
        return st.session_state[self.clave_estado]

    def reiniciar(self) -> None:
        """
        Restablece el estado del botón a False.

        Esto permite que el botón pueda ser presionado y detectado nuevamente.
        """
        st.session_state[self.clave_estado] = False


class SelectorFechasEvento:
    """
    Clase encargada de manejar la selección, validación y cálculo del rango de fechas.

    Al confirmar, guarda automáticamente los valores en st.session_state.

    Attributes:
        fecha_inicio (date): Fecha seleccionada de inicio.
        fecha_fin (date): Fecha seleccionada de fin.
        dias (int): Número de días entre inicio y fin, ambos inclusive.
        mes (str): Mes capitalizado de la fecha de inicio.
        es_valido (bool): Si el rango de fechas es válido.
        confirmado (bool): Si el usuario confirmó el rango de fechas.
    """

    def __init__(self):
        self.fecha_inicio = datetime.today().date()
        self.fecha_fin = datetime.today().date()
        self.dias = 0
        self.mes = ""
        self.es_valido = False
        self.confirmado = False

    def mostrar_controles(self):
        """
        Despliega los controles de selección de fechas y calcula los valores si son válidos.
        """
        st.markdown("## Seleccione fecha de inicio y fin del evento")
        col1, col2 = st.columns(2)

        with col1:
            self.fecha_inicio = st.date_input(
                "📅 Fecha de inicio", value=self.fecha_inicio
            )

        with col2:
            self.fecha_fin = st.date_input("📅 Fecha de fin", value=self.fecha_fin)

        if self.fecha_fin < self.fecha_inicio:
            st.error("❌ La fecha de fin no puede ser anterior a la de inicio.")
            self.es_valido = False
            return

        self.dias = (self.fecha_fin - self.fecha_inicio).days + 1
        self.mes = self.fecha_inicio.strftime("%B").capitalize()
        self.es_valido = True

        st.success(f"✅ Fechas válidas. El rango es de {self.dias} días.")
        st.info(f"📆 El mes de la fecha de inicio es: **{self.mes}**")

    def confirmar(self, boton: "ButtonTracker"):
        """
        Procesa la confirmación del botón si el rango de fechas es válido.
        Guarda los resultados en session_state si se confirma.

        Args:
            boton (ButtonTracker): Instancia del botón a utilizar para la confirmación.
        """
        if self.es_valido and boton.fue_presionado():
            self.confirmado = True
            self._guardar_en_session_state()
            st.success("🟢 Fechas confirmadas exitosamente.")

    def obtener_resultado(self):
        """
        Devuelve los datos de las fechas si han sido confirmadas.

        Returns:
            dict | None: Diccionario con fecha_inicio, fecha_fin, dias y mes si confirmado; None en caso contrario.
        """
        if self.confirmado:
            return {
                "fecha_inicio": self.fecha_inicio,
                "fecha_fin": self.fecha_fin,
                "dias": self.dias,
                "mes": self.mes,
            }
        return None

    def _guardar_en_session_state(self):
        """
        Guarda los valores confirmados en st.session_state con claves estándar.
        """
        st.session_state["fecha_inicio_evento"] = self.fecha_inicio
        st.session_state["fecha_fin_evento"] = self.fecha_fin
        st.session_state["dias_evento"] = self.dias
        st.session_state["mes_evento"] = self.mes
