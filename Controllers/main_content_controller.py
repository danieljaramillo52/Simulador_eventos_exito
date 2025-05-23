import streamlit as st
from services.data_service import GestorDatos
from ui_components.ui_components import (
    ButtonTracker,
    MultiVisibilityController,
    SelectBoxManager,
    SelectorFechasEvento,
    TextInputManager,
    add_key_ss_st,
    set_key_ss_st,
)
from ui_components.utils import formatear_fecha


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
        dict_herra_conp = self.gestor_datos.config["cnf_concep_herr"]

        if visib_sec_her_concep.esta_visible():
            st.write("## Concepto y Herramienta")

            input_concepto = SelectBoxManager(
                clave="text_input_concepto",
                etiqueta="Ingrese el nombre del concepto",
                opciones=dict_herra_conp["concepto"],
                usar_sidebar=False,
            )

            input_herramienta = SelectBoxManager(
                clave="text_input_herramienta",
                etiqueta="Ingrese el nombre de la herramienta",
                opciones=dict_herra_conp["herramienta"],
                usar_sidebar=False,
            )

            btn_confirmar = ButtonTracker(
                clave="btn_confirmar_herramienta_Concepto",
                etiqueta="✅ Confirmar herramienta y concepto",
                usar_sidebar=False,
            )

            if (
                btn_confirmar.fue_presionado()
                and input_herramienta.is_valid()
                and input_concepto.is_valid()
            ):
                set_key_ss_st("herramienta_confirmada", input_herramienta.get_value())
                set_key_ss_st("concepto_confirmado", input_concepto.get_value())

                btn_confirmar.reiniciar()
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

            btn_confirmar = ButtonTracker(
                clave="btn_confirmar_fechas",
                etiqueta="✅ Confirmar fecha",
                usar_sidebar=False,
            )

            if btn_confirmar.fue_presionado():
                set_key_ss_st("fechas_confirmadas", resultado_fecha)
                visib_sec_fechas.ocultar()
                st.rerun()

    def _gestionar_materiales(self):
        """
        Gestiona la selección de materiales y su rango de descuento.

        Si el usuario confirma los valores seleccionados y válidos, los almacena en el estado de sesión
        bajo la clave `materiales_confirmados`, y reinicia los componentes para evitar entradas duplicadas.
        """
        add_key_ss_st(clave="materiales_confirmados", valor_inicial={})
        visib_sec_mat = MultiVisibilityController(
            claves=["text_input_rango", "selector_material", "btn_confirmar_material"]
        )

        if visib_sec_mat.esta_visible():
            st.write("## Materiales")

            selector_material = SelectBoxManager(
                clave="selector_material",
                etiqueta="Seleccione un material",
                opciones=list(
                    self.gestor_datos.df_prec_vtas_procesado["concat_plu_producto"].unique()
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

            btn_confirmar = ButtonTracker(
                clave="btn_confirmar_material",
                etiqueta="✅ Confirmar",
                usar_sidebar=False,
            )

            if (
                btn_confirmar.fue_presionado()
                and selector_material.is_valid()
                and input_rango.is_valid()
            ):
                set_key_ss_st(
                    clave="materiales_confirmados",
                    valor={
                        "material": selector_material.get_value(),
                        "rango": input_rango.get_value(),
                    },
                )
                btn_confirmar.reiniciar()
                selector_material.reset()
                input_rango.reset()
                visib_sec_mat.ocultar()
                st.rerun()

    def ejecutar_contenido_principal(self):
        """
        Ejecuta todas las secciones del contenido principal:

        - Materiales y su rango de descuento
        - Herramienta y concepto
        - Fechas

        Al finalizar, consolida todos los valores confirmados en una sola estructura
        almacenada en st.session_state bajo la clave dict_herra_conp_fecha.
        También imprime el resultado al usuario para su verificación.
        """

        self._gestionar_materiales()
        self._gestionar_herramienta_concepto()
        self._gestionar_fechas()

        dict_final = {
            "concat_plu_producto": st.session_state.get(
                "materiales_confirmados", {}
            ).get("material"),
            "rango": st.session_state.get("materiales_confirmados", {}).get("rango"),
            "Herramienta": st.session_state.get("herramienta_confirmada", ""),
            "Concepto": st.session_state.get("concepto_confirmado", ""),
            "Fecha": formatear_fecha(
                st.session_state.get("fechas_confirmadas", None),
            ),
        }

        set_key_ss_st("dict_herra_conp_fecha", dict_final)

        return dict_final
