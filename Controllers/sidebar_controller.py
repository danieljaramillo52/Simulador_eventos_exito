import streamlit as st
from ui_components.ui_components import (
    set_key_ss_st,
    SelectBoxManager,
    TextInputManager,
    ButtonTracker,
    FileUploaderManager,
)

from pandas import DataFrame
from typing import Tuple, Optional, Dict, Any


class ControladorBarraLateral:
    """Clase que gestiona todos los componentes de la barra lateral"""

    def __init__(self, config_lv: Dict[str, Any]):
        """
        Args:
            config (Dict): Configuración cargada desde el archivo de configuración
        """
        self.config_lv = config_lv

    def _renderizar_seccion_descuentos(self) -> str:
        """Renderiza los componentes para selección de rango de descuentos

        Returns:
            str: Rango de descuento seleccionado
        """
        st.sidebar.divider()
        st.sidebar.markdown("## Rango de descuentos")

        cnfg_select_box_lv = self.config_lv["seccion_rango_descuento"]["select_box_rng"]

        selector_rango = SelectBoxManager(
            clave=cnfg_select_box_lv["clave"],
            etiqueta=cnfg_select_box_lv["etiqueta"],
            opciones=cnfg_select_box_lv["list_rng_dctos"],
            usar_sidebar=True,
        )

        cnfg_btn_confirmar_rng_lv = self.config_lv["seccion_rango_descuento"][
            "btn_confirmar_rng"
        ]

        btn_confirmar = ButtonTracker(
            clave=cnfg_btn_confirmar_rng_lv["clave"],
            etiqueta=cnfg_btn_confirmar_rng_lv["etiqueta"],
            usar_sidebar=True,
        )

        if btn_confirmar.fue_presionado() and selector_rango.is_valid():
            set_key_ss_st("rango_act", selector_rango.get_value())
            btn_confirmar.reiniciar()
            st.sidebar.success("✅ Rango confirmado")

        return st.session_state.get("rango_act", "")

    def _renderizar_seccion_crecimiento(self) -> int:
        """Renderiza los componentes para entrada de porcentaje de crecimiento

        Returns:
            int: Porcentaje de crecimiento ingresado
        """
        st.sidebar.markdown("## Porcentaje de crecimiento")

        cfg_input_cre = self.config_lv["seccion_crecimiento"]["text_input_crec"]

        input_crecimiento = TextInputManager(
            clave=cfg_input_cre["clave"],
            etiqueta=cfg_input_cre["etiqueta"],
            valor_por_defecto=cfg_input_cre["valor_por_defecto"],
            tipo=int,
            minimo=cfg_input_cre["minimo"],
            maximo=cfg_input_cre["maximo"],
            usar_sidebar=True,
        )

        cnfg_btn_confirm_porcentaje_cre_lv = self.config_lv["seccion_crecimiento"][
            "btn_confirmar_rng"
        ]

        btn_confirmar = ButtonTracker(
            clave=cnfg_btn_confirm_porcentaje_cre_lv["clave"],
            etiqueta=cnfg_btn_confirm_porcentaje_cre_lv["etiqueta"],
            usar_sidebar=True,
        )

        if btn_confirmar.fue_presionado() and input_crecimiento.is_valid():
            set_key_ss_st("portje_cremto_act", input_crecimiento.get_value())
            btn_confirmar.reiniciar()
            st.sidebar.success("✅ % de crecimiento confirmado")

        return st.session_state.get("portje_cremto_act", 10)

    def _renderizar_cargador_archivos(self):
        """Renderiza el componente para carga de archivos

        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración

        Returns:
            Optional[pd.DataFrame]: DataFrame con los datos cargados o None
        """
        cfg_archivo = self.config_lv["seccion_archivo"]["file_uploader"]

        gestor_archivos = FileUploaderManager(
            titulo=cfg_archivo["titulo"],
            clave=cfg_archivo["clave"],
            uploader_msg=cfg_archivo["uploader_msg"],
            limit_msg=cfg_archivo["limit_msg"],
            button_msg=cfg_archivo["button_msg"],
            tipo_archivos=cfg_archivo["tipo_archivos"],
            icon=cfg_archivo["icon"],
            usar_sidebar=True,
        )

        if gestor_archivos.uploaded_files():
            return gestor_archivos.leer_archivos()[0]
        return None

    def controlador_barra_lateral(self) -> Tuple[str, int, Optional[DataFrame]]:
        """Controlador principal de la barra lateral

        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración

        Returns:
            Tuple: Tupla con (rango_actual, porcentaje_crecimiento, dataframe)
        """
        st.sidebar.title(self.config_lv["encabezado"])
        rango_actual = self._renderizar_seccion_descuentos()
        crecimiento_actual = self._renderizar_seccion_crecimiento()
        df = self._renderizar_cargador_archivos()
        return rango_actual, crecimiento_actual, df
