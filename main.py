import streamlit as st
import utils
from ui_components import (
    SelectBoxManager,
    TextInputManager,
    ButtonTracker,
    set_key_session_state,
    add_key_session_state,
    FileUploaderManager,
    SelectorFechasEvento,
    MultiVisibilityController,
)
from pandas import DataFrame
from config_loader import ConfigLoader
from typing import Dict, Any, Tuple, Optional


class ControladorBarraLateral:
    """Clase que gestiona todos los componentes de la barra lateral"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config (Dict): Configuración cargada desde el archivo de configuración
        """
        self.config = config
        self.titulo = config["encabezado"]
        self.list_rango_descuento = config["rango_descuento"]
        self.enczdo_rang_dcto = config["enczdo_rang_dcto"]

    def _renderizar_seccion_descuentos(self) -> str:
        """Renderiza los componentes para selección de rango de descuentos

        Returns:
            str: Rango de descuento seleccionado
        """
        st.sidebar.divider()
        st.sidebar.markdown("## Rango de descuentos")

        selector_rango = SelectBoxManager(
            clave="selector_rango_dcto",
            etiqueta=self.enczdo_rang_dcto,
            opciones=self.list_rango_descuento,
            usar_sidebar=True,
        )

        boton_confirmar = ButtonTracker(
            clave="btn_confirmar_rango", etiqueta="Confirmar rango %", usar_sidebar=True
        )

        if boton_confirmar.fue_presionado() and selector_rango.is_valid():
            set_key_session_state("rango_act", selector_rango.get_value())
            boton_confirmar.reiniciar()

        return st.session_state.get("rango_act", "")

    def _renderizar_seccion_crecimiento(self) -> int:
        """Renderiza los componentes para entrada de porcentaje de crecimiento

        Returns:
            int: Porcentaje de crecimiento ingresado
        """
        st.sidebar.markdown("## Porcentaje de crecimiento")

        input_crecimiento = TextInputManager(
            clave="text_input_crecimiento",
            etiqueta="Ingrese % de crecimiento:",
            valor_por_defecto=10,
            tipo=int,
            minimo=1,
            maximo=50,
            usar_sidebar=True,
        )

        boton_confirmar = ButtonTracker(
            clave="btn_confirmar_%_crecimiento",
            etiqueta="Confirmar % crecimiento",
            usar_sidebar=True,
        )

        if boton_confirmar.fue_presionado() and input_crecimiento.is_valid():
            set_key_session_state("portje_cremto_act", input_crecimiento.get_value())
            boton_confirmar.reiniciar()

        return st.session_state.get("portje_cremto_act", 10)

    def _renderizar_cargador_archivos(
        self, config_loader: ConfigLoader
    ) -> Optional["DataFrame"]:
        """Renderiza el componente para carga de archivos

        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración

        Returns:
            Optional[pd.DataFrame]: DataFrame con los datos cargados o None
        """
        gestor_archivos = FileUploaderManager(
            titulo="Cargar archivo",
            clave="archivo_excel",
            uploader_msg="📤 Adjuntar archivo Excel",
            limit_msg="Tamaño máximo 200MB",
            button_msg="🗂️ Examinar",
            tipo_archivos=["csv", "xlsx"],
            icon="MdUploadFile",
            usar_sidebar=True,
            use_cols=[*config_loader.config["df_insumo"]["dict_cols"]],
        )

        if gestor_archivos.uploaded_files():
            return gestor_archivos.leer_archivos()[0]
        return None

    def controlador_barra_lateral(
        self, config_loader: ConfigLoader
    ) -> Tuple[str, int, Optional[DataFrame]]:
        """Controlador principal de la barra lateral

        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración

        Returns:
            Tuple: Tupla con (rango_actual, porcentaje_crecimiento, dataframe)
        """
        st.sidebar.title(self.titulo)
        rango_actual = self._renderizar_seccion_descuentos()
        crecimiento_actual = self._renderizar_seccion_crecimiento()
        df = self._renderizar_cargador_archivos(config_loader)
        return rango_actual, crecimiento_actual, df


class GestorContenidoPrincipal:
    """
    Clase que gestiona la visualización e interacción del contenido principal de la aplicación Streamlit.

    Esta clase organiza el flujo de entrada de datos del usuario mediante inputs, selectores y botones,
    manejando la lógica de confirmación y almacenamiento en `st.session_state` únicamente cuando el usuario
    confirma los datos correspondientes.
    """

    def __init__(self, gestor_datos: "GestorDatos"):
        """
        Inicializa el gestor con una instancia de manejo de datos procesados.

        Args:
            gestor_datos (GestorDatos): Objeto que contiene el DataFrame procesado y los rangos válidos.
        """
        self.gestor_datos = gestor_datos

    def _gestionar_herramienta_concepto(self):
        """
        Gestiona la sección de entrada de texto para herramienta y concepto.

        Si el usuario presiona el botón de confirmación y los campos son válidos, almacena los valores
        en el estado de sesión bajo las claves `herramienta_confirmada` y `concepto_confirmado`, y reinicia los componentes.
        """
        visib_sec_her_concep = MultiVisibilityController(
            claves=[
                "btn_confirmar_herramienta_Concepto",
                "text_input_herramienta",
                "text_input_concepto",
            ]
        )

        st.write("## Herramienta y Concepto")

        if visib_sec_her_concep.esta_visible():
            input_herramienta = TextInputManager(
                clave="text_input_herramienta",
                etiqueta="Ingrese el nombre de la herramienta",
                tipo=str,
                usar_sidebar=False,
            )

            input_concepto = TextInputManager(
                clave="text_input_concepto",
                etiqueta="Ingrese el nombre del concepto",
                tipo=str,
                usar_sidebar=False,
            )

            boton_confirmar = ButtonTracker(
                clave="btn_confirmar_herramienta_Concepto",
                etiqueta="✅ Confirmar herramienta y concepto",
                usar_sidebar=False,
            )

            if (
                boton_confirmar.fue_presionado()
                and input_herramienta.is_valid()
                and input_concepto.is_valid()
            ):
                set_key_session_state(
                    "herramienta_confirmada", input_herramienta.get_value()
                )
                set_key_session_state("concepto_confirmado", input_concepto.get_value())

                boton_confirmar.reiniciar()
                input_herramienta.reset()
                input_concepto.reset()
                visib_sec_her_concep.ocultar()
                st.rerun()

    def _gestionar_fechas(self):
        """
        Gestiona la selección de fechas de inicio y fin mediante un componente personalizado.

        Al confirmar la selección, almacena el resultado en `st.session_state` bajo la clave `fechas_confirmadas`.
        """
        visib_sec_fechas = MultiVisibilityController(
            claves=["btn_confirmar_fechas", "📅 Fecha de inicio", "📅 Fecha de fin"]
        )

        if visib_sec_fechas.esta_visible():
            selector_fechas = SelectorFechasEvento()
            selector_fechas.mostrar_controles()
            resultado_fecha = selector_fechas.obtener_resultado()

            boton_confirmar = ButtonTracker(
                clave="btn_confirmar_fechas",
                etiqueta="✅ Confirmar fecha",
                usar_sidebar=False,
            )

            if boton_confirmar.fue_presionado():
                set_key_session_state("fechas_confirmadas", resultado_fecha)
                visib_sec_fechas.ocultar()
                st.rerun()

    def _gestionar_materiales(self):
        """
        Gestiona la selección de materiales y su rango de descuento.

        Si el usuario confirma los valores seleccionados y válidos, los almacena en el estado de sesión
        bajo la clave `materiales_confirmados`, y reinicia los componentes para evitar entradas duplicadas.
        """
        add_key_session_state(clave="materiales_confirmados", valor_inicial=[])
        visib_sec_mat = MultiVisibilityController(
            claves=["text_input_rango", "selector_material", "btn_confirmar_material"]
        )

        if visib_sec_mat.esta_visible():
            st.write("## Materiales")

            selector_material = SelectBoxManager(
                clave="selector_material",
                etiqueta="Seleccione un material",
                opciones=list(
                    self.gestor_datos.df_procesado["concat_plu_producto"].unique()
                ),
                usar_sidebar=False,
            )

            input_rango = TextInputManager(
                clave="text_input_rango",
                etiqueta="Seleccione un rango de descuento:",
                valor_por_defecto=10,
                tipo=int,
                minimo=self.gestor_datos.rango_valido[0],
                maximo=self.gestor_datos.rango_valido[1],
                usar_sidebar=False,
            )

            boton_confirmar = ButtonTracker(
                clave="btn_confirmar_material",
                etiqueta="✅ Confirmar",
                usar_sidebar=False,
            )

            if (
                boton_confirmar.fue_presionado()
                and selector_material.is_valid()
                and input_rango.is_valid()
            ):
                set_key_session_state(
                    clave="materiales_confirmados",
                    valor={
                        "material": selector_material.get_value(),
                        "rango": input_rango.get_value(),
                    },
                )
                boton_confirmar.reiniciar()
                selector_material.reset()
                input_rango.reset()
                visib_sec_mat.ocultar()
                st.rerun()

    def ejecutar_contenido_principal(self):
        """
        Ejecuta todas las secciones del contenido principal:

        Permite al usuario registrar múltiples combinaciones de:
        - Material + rango
        - Herramienta + concepto
        - Fechas

        Cada vez que el usuario presiona '➕ Agregar combinación', se añade un registro
        al historial almacenado en `st.session_state["lista_combinaciones"]`.
        """

        self._gestionar_materiales()
        self._gestionar_herramienta_concepto()
        self._gestionar_fechas()

        # Botón para confirmar y agregar una nueva combinación
        if st.button("➕ Agregar combinación"):
            nueva_comb = {
                "material": st.session_state.get("materiales_confirmados", {}).get("material"),
                "rango": st.session_state.get("materiales_confirmados", {}).get("rango"),
                "Herramienta": st.session_state.get("herramienta_confirmada", ""),
                "Concepto": st.session_state.get("concepto_confirmado", ""),
                "Fecha": st.session_state.get("fechas_confirmadas", None),
            }

            # Validación mínima (evita registros vacíos)
            if all([nueva_comb["material"], nueva_comb["rango"], nueva_comb["Herramienta"], nueva_comb["Concepto"], nueva_comb["Fecha"]]):
                if "lista_combinaciones" not in st.session_state:
                    st.session_state["lista_combinaciones"] = []
                st.session_state["lista_combinaciones"].append(nueva_comb)
                st.success("✅ Combinación registrada exitosamente.")
                st.rerun()
            else:
                st.warning("⚠️ Por favor completa todos los campos antes de agregar una combinación.")

        # Mostrar todas las combinaciones registradas
        if "lista_combinaciones" in st.session_state:
            st.write("### 📝 Combinaciones registradas:")
            for i, item in enumerate(st.session_state["lista_combinaciones"], start=1):
                st.markdown(f"**{i}.** {item}")



class GestorDatos:
    """Clase para manejar toda la lógica relacionada con datos"""

    def __init__(self, config_loader: ConfigLoader):
        """
        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración
        """
        self.config = config_loader.config
        self.df_crudo = None
        self.df_procesado = None
        self.rango_valido = (1, 50)

    def cargar_datos(self, df: Optional[DataFrame]):
        """Carga y procesa los datos de entrada

        Args:
            df (Optional[pd.DataFrame]): DataFrame con datos crudos
        """
        if df is not None and not df.empty:
            add_key_session_state(clave="df_insumo", valor_inicial=df)
            self.df_crudo = df.copy()
            self._procesar_datos()

    def _procesar_datos(self):
        """Realiza transformaciones básicas en los datos"""
        self.df_procesado = utils.concatenar_columnas_pd(
            dataframe=self.df_crudo,
            cols_elegidas=["plu", "producto"],
            nueva_columna="concat_plu_producto",
            usar_separador=True,
            separador=" : ",
        )

    def validar_rango(self, texto_rango: str):
        """Valida y extrae rango numérico de un texto

        Args:
            texto_rango (str): Texto conteniendo el rango (ej: "10-20%")
        """
        self.rango_valido = utils.obtener_rango_valido_desde_texto(texto_rango)


class Aplicacion:
    """Clase principal que controla el flujo de la aplicación"""

    def __init__(self):
        self.cargador_config = ConfigLoader(utils=utils)
        self.barra_lateral = ControladorBarraLateral(
            self.cargador_config.cnf_lateral_var
        )
        self.gestor_datos = GestorDatos(self.cargador_config)
        self.contenido_principal = GestorContenidoPrincipal(self.gestor_datos)

    def ejecutar(self):
        """Método principal que ejecuta la aplicación"""
        # Configuración de barra lateral
        rango_act, portje_cremto_act, df_insumo = (
            self.barra_lateral.controlador_barra_lateral(self.cargador_config)
        )

        # Procesamiento de datos
        self.gestor_datos.validar_rango(rango_act)
        self.gestor_datos.cargar_datos(df_insumo)

        # Contenido principal
        if self.gestor_datos.df_procesado is not None:
            self.contenido_principal.ejecutar_contenido_principal()
        else:
            st.warning("⚠️ Aún no se ha cargado un archivo de insumos.")
            st.stop()


if __name__ == "__main__":
    utils.setup_ui()
    Aplicacion().ejecutar()
