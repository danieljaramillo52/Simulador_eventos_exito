import streamlit as st
import re
import utils
from ui_components import (
    SelectBoxManager,
    TextInputManager,
    ButtonTracker,
    set_key_session_state,
    add_key_session_state,
    FileUploaderManager,
    SelectorFechasEvento,
)
from config_loader import ConfigLoader


# ssesion.state es un diccionario que guarda el estado actual de cada variable.


class ControladorBarraLateral:
    def __init__(self, config_loader: ConfigLoader):

        # Configuración barra lateral
        self.cnf_lateral_var = config_loader.cnf_lateral_var

        # Crea un titulo para la barra lateral
        self.titulo = self.cnf_lateral_var["encabezado"]
        self.enczdo_rang_dcto = self.cnf_lateral_var["enczdo_rang_dcto"]

        # Tomamos los rangos de descuentos.
        self.list_rango_descuento = self.cnf_lateral_var["rango_descuento"]

    def controlador_barra_lateral(self, config_loader):
        df = None

        # Titulo continuo de la barra.
        st.sidebar.title(self.titulo)

        st.sidebar.divider()

        st.sidebar.markdown("## Rango de descuentos.")

        # Leer widgets con valores por defecto desde session_state
        box_manager_menu = SelectBoxManager(
            clave=self.titulo,
            etiqueta=self.enczdo_rang_dcto,
            opciones=self.list_rango_descuento,
            usar_sidebar=True,
        )
        btn_confirmar_rango = ButtonTracker(
            clave="btn_confirmar_rango",
            etiqueta="Confirmar rango %",
            usar_sidebar=True,
        )

        if btn_confirmar_rango.fue_presionado() and box_manager_menu.is_valid():
            # Guardamos los valores obtenidos en la sesion_sta
            set_key_session_state(clave="rango_act", valor=box_manager_menu.get())
            box_manager_menu.get()
            btn_confirmar_rango.reiniciar()

        st.sidebar.markdown("## Rango de descuentos.")

        text_input_crecimiento = TextInputManager(
            clave="text_input_crecimiento",
            etiqueta="Ingrese % de crecimiento:",
            valor_por_defecto=10,
            tipo=int,
            minimo=1,
            maximo=50,
            usar_sidebar=True,
        )

        btn_confirmar_crecimiento = ButtonTracker(
            clave="btn_confirmar_%_crecimiento",
            etiqueta="Confirmar % crecimiento",
            usar_sidebar=True,
        )

        if (
            btn_confirmar_crecimiento.fue_presionado()
            and text_input_crecimiento.is_valid()
        ):
            set_key_session_state(
                clave="portje_cremto_act", valor=text_input_crecimiento.get_value()
            )
            btn_confirmar_crecimiento.reiniciar()

        # Adjuntar los archivos de excel necesarios.
        file_manager = FileUploaderManager(
            titulo="Ajuntar archivo",
            clave="archivo_excel",
            uploader_msg="📤 Adjuntar archivo Excel",
            limit_msg="Tamaño máximo 200MB",
            button_msg="🗂️ Examinar",
            tipo_archivos=["csv", "xlsx"],
            icon="MdUploadFile",  # Puedes usar cualquier icono de Material Design Icons
            usar_sidebar=True,
            use_cols=[*config_loader.config["df_insumo"]["dict_cols"]],
        )
        if file_manager.uploaded_files():
            dataframes = file_manager.leer_archivos()
            df = dataframes[0]

        # Obtener los valores actuales de rango y porcentaje.
        rango_act = st.session_state.get("rango_act", "")
        portje_cremto_act = st.session_state.get("portje_cremto_act", "")

        return rango_act, portje_cremto_act, df


dict_herra_conp_fecha = {}


class StreamlitApp:
    def __init__(self):
        self.config_loader = ConfigLoader(utils=utils)
        self.dict_df_cols = self.config_loader.dict_cols
        self.rango_act = None
        self.portje_cremto_act = None
        self.df_insumo = None

    def run(self):
        self._cargar_barra_lateral()
        self._gestionar_estado_herramienta_concepto()
        self._gestionar_fechas()
        self._cargar_insumo()
        self._gestionar_materiales()

    def _cargar_barra_lateral(self):
        barra = ControladorBarraLateral(config_loader=self.config_loader)
        self.rango_act, self.portje_cremto_act, self.df_insumo = (
            barra.controlador_barra_lateral(config_loader=self.config_loader)
        )

    def _gestionar_estado_herramienta_concepto(self):
        add_key_session_state(
            "dict_herra_conp_fecha", {"Herramienta": "", "Concepto": "", "Fecha": []}
        )
        dict_herra_conp_fecha = st.session_state["dict_herra_conp_fecha"]

        text_input_herramienta = TextInputManager(
            "text_input_herramienta",
            "Ingrese el nombre de la herramienta",
            tipo=str,
            usar_sidebar=False,
        )
        text_input_concepto = TextInputManager(
            "text_input_concepto",
            "Ingrese el nombre del concepto",
            tipo=str,
            usar_sidebar=False,
        )
        btn_confirmar_datos = ButtonTracker(
            "btn_confirmar_herramienta_Concepto",
            etiqueta="✅ Confirmar herramienta y concepto",
            usar_sidebar=False,
        )

        if (
            btn_confirmar_datos.fue_presionado()
            and text_input_herramienta.is_valid()
            and text_input_concepto.is_valid()
        ):
            dict_herra_conp_fecha["Herramienta"] = text_input_herramienta.get_value()
            dict_herra_conp_fecha["Concepto"] = text_input_concepto.get_value()
            st.session_state["dict_herra_conp_fecha"] = dict_herra_conp_fecha

            btn_confirmar_datos.reiniciar()
            text_input_concepto.reset()
            text_input_herramienta.reset()

    def _gestionar_fechas(self):
        dict_herra_conp_fecha = st.session_state["dict_herra_conp_fecha"]
        selector_fechas = SelectorFechasEvento()
        selector_fechas.mostrar_controles()
        selector_fechas.confirmar(boton=ButtonTracker(clave="btn_confirmar_fechas"))

        resultado_fecha = selector_fechas.obtener_resultado()
        if resultado_fecha:
            dict_herra_conp_fecha["Fecha"].append(resultado_fecha)
            st.session_state["dict_herra_conp_fecha"] = dict_herra_conp_fecha
            for clave in [
                "fecha_inicio_evento",
                "fecha_fin_evento",
                "dias_evento",
                "mes_evento",
            ]:
                st.session_state.pop(clave, None)
            st.success("🗓️ Fecha registrada. Puedes ingresar otra si lo deseas.")
            st.write(dict_herra_conp_fecha)

    def _cargar_insumo(self):
        if self.df_insumo is not None and not self.df_insumo.empty:
            add_key_session_state(clave="df_insumo", valor_inicial=self.df_insumo)
        else:
            self.df_insumo = st.session_state.get("df_insumo")

        if self.df_insumo is None or self.df_insumo.empty:
            st.warning("⚠️ Aún no se ha cargado un archivo de insumos.")
            st.stop()

        self.df_insumo_copy = self.df_insumo.copy()
        self.df_insumo_copy = utils.concatenar_columnas_pd(
            dataframe=self.df_insumo_copy,
            cols_elegidas=["plu", "producto"],
            nueva_columna="concat_plu_producto",
            usar_separador=True,
            separador=" : ",
        )

    def _gestionar_materiales(self):
        if "materiales_confirmados" not in st.session_state:
            st.session_state["materiales_confirmados"] = []
        if "finalizado" not in st.session_state:
            st.session_state["finalizado"] = False

        if st.session_state["finalizado"]:
            st.success("✅ Has finalizado la selección de materiales.")
            for idx, item in enumerate(
                st.session_state["materiales_confirmados"], start=1
            ):
                cols = st.columns([0.9, 0.1])
                with cols[0]:
                    st.markdown(f"{idx}. **{item['material']}** — {item['rango']}")
                with cols[1]:
                    if st.button(f"❌", key=f"eliminar_material_{idx}"):
                        st.session_state["materiales_confirmados"].pop(idx - 1)
                        st.rerun()
            if "df_insumo_resultado" not in st.session_state:
                st.session_state["df_insumo_resultado"] = utils.procesar_insumo(
                    df_insumo=self.df_insumo_copy,
                    porcentaje_crecimiento=self.portje_cremto_act,
                    lista_materiales=st.session_state["materiales_confirmados"],
                    dict_cols=self.dict_df_cols,
                )
            st.markdown("### 📊 Resultados del procesamiento")
            st.dataframe(st.session_state["df_insumo_resultado"])

            if st.button("🔁 Modificar selección de materiales"):
                st.session_state["finalizado"] = False
                st.session_state.pop("df_insumo_resultado", None)
                st.rerun()
        else:
            num_material = len(st.session_state["materiales_confirmados"]) + 1
            st.markdown(f"### Material #{num_material}")

            box_material = SelectBoxManager(
                clave="selector_material",
                etiqueta="Seleccione un material",
                opciones=list(self.df_insumo_copy["concat_plu_producto"].unique()),
                usar_sidebar=False,
            )

            try:
                numeros = tuple(map(int, re.findall(r"\d+", self.rango_act)))
                if len(numeros) < 2:
                    numeros = (5, 10)
            except:
                numeros = (5, 10)

            text_input_rango = TextInputManager(
                clave="text_input_rango",
                etiqueta="Seleccione un rango de descuento:",
                valor_por_defecto=10,
                tipo=int,
                minimo=numeros[0],
                maximo=numeros[1],
                usar_sidebar=False,
            )

            btn_confirmar = ButtonTracker(
                clave="btn_confirmar_material",
                etiqueta="✅ Confirmar",
                usar_sidebar=False,
            )

            if (
                btn_confirmar.fue_presionado()
                and box_material.is_valid()
                and text_input_rango.is_valid()
            ):
                st.session_state["materiales_confirmados"].append(
                    {
                        "material": box_material.get(),
                        "rango": text_input_rango.get_value(),
                    }
                )
                btn_confirmar.reiniciar()
                box_material.reset()
                text_input_rango.reset()
                st.rerun()

            if st.button("🚫 Finalizar selección"):
                st.session_state["finalizado"] = True
                st.rerun()


if __name__ == "__main__":
    utils.setup_ui()
    app = StreamlitApp()
    app.run()
