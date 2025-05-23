from pandas import DataFrame
import streamlit as st
from ui_components.ui_components import (
    ButtonTracker,
    add_key_ss_st,
    clean_key_ss_st,
    set_key_ss_st,
    set_multiple_keys,
)
import ui_components.utils as utils
from Controllers.sidebar_controller import ControladorBarraLateral
from Controllers.main_content_controller import GestorContenidoPrincipal
from services.data_service import GestorDatos
from config_loader import ConfigLoader


class Aplicacion:
    """Clase principal que controla el flujo de la aplicación"""

    def __init__(self) -> None:
        """
        Inicializa las instancias necesarias para el funcionamiento de la aplicación,
        incluyendo la carga de configuración, la barra lateral, los datos y el contenido principal.
        """
        self.cargador_config = ConfigLoader(utils=utils)
        self.barra_lateral = ControladorBarraLateral(
            config_lv=self.cargador_config.cnf_lateral_var
        )
        self.gestor_datos = GestorDatos(self.cargador_config)
        self.contenido_principal = GestorContenidoPrincipal(self.gestor_datos)

    def ejecutar(self) -> None:
        """
        Ejecuta el ciclo principal de la aplicación. Controla la lógica de:
        - Inicialización de estado
        - Procesamiento de barra lateral
        - Registro de materiales
        - Edición de registros
        - Cálculo y visualización de resultados
        """
        # Inicializar variables en session_state si aún no existen
        self._inicializar_session()

        # Procesar selección de barra lateral
        rango_act, portje_cremto_act, df_precios, df_vtas = self._procesar_barra_lateral()

        # Validar rango y cargar archivo
        self.gestor_datos.validar_rango(rango_act)
        
        # Bnadera para archivos cargados
        add_key_ss_st(clave="archivos_cargados", valor_inicial=False)
        self.gestor_datos.procesar_dfs_insumos(df_precios, df_vtas)
        
        df_procesado_prec_vtas = self.gestor_datos.df_prec_vtas_procesado
        set_key_ss_st(clave="archivos_cargados", valor=True)

        # Si hay insumo cargado, mostrar sección de registro de materiales
        if df_procesado_prec_vtas is not None:
            self._gestionar_registro_material()

        # Si se confirmó un registro, mostrar tabla editable
        if st.session_state.get("registro_confirmado", False):
            self._editar_materiales()

        # Si se confirmó la edición, calcular y mostrar resultados
        if st.session_state.get("edicion_confirmada", False):
            df_procesado_final = self._calcular_resultados(
                df_procesado_prec_vtas, portje_cremto_act
            )
            self._mostrar_promedios(df_procesado_final)

        # Si no hay insumos cargados, mostrar advertencia
        elif st.session_state["archivos_cargados"] == False:
            st.warning(self.cargador_config.cnf_mensajes["sin_insumos"])
            st.stop()

    def _inicializar_session(self) -> None:
        """
        Inicializa las claves necesarias en el session_state según la configuración definida.
        """
        for clave, opciones in self.cargador_config.cnf_session_keys.get(
            "inicializacion", {}
        ).items():
            add_key_ss_st(clave, opciones["valor_inicial"])

    def _procesar_barra_lateral(self) -> tuple[str, float, DataFrame]:
        """
        Llama al controlador de la barra lateral para obtener:
        - Rango seleccionado
        - Porcentaje de crecimiento
        - DataFrame cargado desde archivo

        Returns:
            *
        """
        return self.barra_lateral.controlador_barra_lateral()

    def _gestionar_registro_material(self) -> None:
        """
        Maneja la lógica del registro de un nuevo material:
        - Ejecuta el contenido principal
        - Espera confirmación del usuario
        - Actualiza session_state con el material registrado
        - Reemplaza claves no necesarias
        """
        # Instanciar botones desde configuración
        cfg_boton = self.cargador_config.cnf_botones["agregar_material"]
        boton_agregar_material = ButtonTracker(**cfg_boton)

        cfg_confirmar = self.cargador_config.cnf_botones["confirmar_registro"]
        boton_confirmar_registro = ButtonTracker(**cfg_confirmar)

        # Si se presiona "Agregar material", se ejecuta el contenido principal
        if boton_agregar_material.fue_presionado():
            # Reinicio de estado antes de confirmar
            set_multiple_keys(
                {
                    "registro_confirmado": False,
                    "edicion_confirmada": False,
                    "confirmar_edicion_pendiente": False,
                }
            )

            # Recolectar los datos ingresados
            dict_final = self.contenido_principal.ejecutar_contenido_principal()
            claves_a_conservar = set(
                self.cargador_config.cnf_session_keys["claves_preservar"]
            )

            # Renderizar y escuchar botón de confirmación
            boton_confirmar_registro._mostrar_boton()
            if boton_confirmar_registro.fue_presionado():
                # Aplanar diccionario para agregar fecha
                dict_final_aplanado = utils.aplanar_diccionario(
                    dict_final, clave_aplanar="Fecha"
                )
                st.session_state["list_materiales"].append(dict_final_aplanado)

                # Crear nuevo DataFrame con los registros acumulados
                df_para_calculos = DataFrame(st.session_state["list_materiales"])

                # Limpiar claves no necesarias
                claves_a_eliminar = [
                    clave
                    for clave in st.session_state.keys()
                    if clave not in claves_a_conservar
                ]
                clean_key_ss_st(keys=claves_a_eliminar)

                # Guardar resultado y confirmar
                set_key_ss_st("df_final", df_para_calculos)
                set_key_ss_st("registro_confirmado", True)
                st.success(self.cargador_config.cnf_mensajes["registro_exitoso"])
                st.rerun()

    def _editar_materiales(self) -> None:
        """
        Permite al usuario editar o eliminar los materiales registrados:
        - Muestra tabla editable
        - Detecta confirmación de edición o eliminación
        - Actualiza el estado y los datos en session_state
        """
        st.subheader(self.cargador_config.cnf_mensajes["editar_titulo"])

        col_eliminar = self.cargador_config.cnf_columnas_data["eliminar_col"]
        col_bloqueada = self.cargador_config.cnf_columnas_data["concat_col"]
        editor_key = self.cargador_config.cnf_session_keys["editor_df_key"]

        # Crear una copia editable del DataFrame actual
        df_edicion = st.session_state["df_final"].copy()
        df_edicion[col_eliminar] = False

        # Mostrar editor interactivo
        df_editado = st.data_editor(
            df_edicion,
            key=editor_key,
            use_container_width=True,
            disabled=[col_bloqueada],
            num_rows="fixed",
        )

        # Botón: Confirmar edición
        btn_conf = self.cargador_config.cnf_botones["confirmar_edicion"]
        if st.button(btn_conf["etiqueta"]):
            set_key_ss_st("confirmar_edicion_pendiente", valor=True)
            # st.session_state["confirmar_edicion_pendiente"] = True
            set_key_ss_st("list_materiales", df_editado.to_dict(orient="records"))
            st.rerun()

        # Botón: Eliminar filas
        btn_del = self.cargador_config.cnf_botones["eliminar_filas"]
        if st.button(btn_del["etiqueta"]):
            df_filtrado = df_editado[df_editado[col_eliminar] == False].drop(
                columns=[col_eliminar]
            )
            set_key_ss_st("df_final", df_filtrado)
            set_key_ss_st("list_materiales", df_filtrado.to_dict(orient="records"))
            st.success(self.cargador_config.cnf_mensajes["eliminacion_exitosa"])
            st.rerun()

        # Confirmar edición si fue activada
        if st.session_state["confirmar_edicion_pendiente"]:
            set_key_ss_st("df_final", df_editado)
            set_key_ss_st("edicion_confirmada", True)
            st.success(self.cargador_config.cnf_mensajes["edicion_exitosa"])
            st.session_state["confirmar_edicion_pendiente"] = False
            st.rerun()

    def _calcular_resultados(
        self, df_procesado_prec_vtas: DataFrame, portje_cremto_act: float
    ) -> DataFrame:
        """
        Realiza el cálculo final del DataFrame procesado:
        - Hace merge con columnas relevantes
        - Aplica transformación usando el porcentaje de crecimiento

        Args:
            df_procesado_prec_vtas (DataFrame): Datos base procesados
            portje_cremto_act (float): Porcentaje de crecimiento

        Returns:
            DataFrame: Resultado final procesado
        """
        columnas = self.cargador_config.cols_df_insumo

        df_merge = utils.left_merge_on_columns(
            df1=st.session_state["df_final"],
            df2=df_procesado_prec_vtas[columnas],
            key_columns=["concat_plu_producto"],
        )

        df_procesado_final = utils.procesar_insumo(
            df_insumo=df_merge,
            porcentaje_crecimiento=portje_cremto_act,
            dict_cols=self.cargador_config.dict_cols,
        )

        return df_procesado_final

    def _mostrar_promedios(self, df_procesado_final: DataFrame) -> None:
        """
        Muestra en pantalla:
        - La tabla final procesada
        - Los promedios de las columnas clave
        - Métricas de resumen

        Args:
            df_procesado_final (DataFrame): DataFrame ya procesado con insumos y cálculos aplicados
        """
        set_key_ss_st("df_procesado_final", df_procesado_final)
        st.dataframe(df_procesado_final.set_index("producto"), use_container_width=True)

        # Mostrar promedios de columnas clave
        st.markdown("### Promedios actuales:")
        sumatoria = utils.calcular_vtas_totales(
            df_procesado_final, ["Venta de la actividad", "Costo del descuento"]
        )

        # Mostrar métricas en columnas separadas
        col1, col2 = st.columns(2)
        col1.metric(
            "💸 Total. Venta de la actividad",
            f"${sumatoria['Venta de la actividad']:,}",
        )
        col2.metric(
            "🔻📉 Total. Costo del descuento", f"${sumatoria['Costo del descuento']:,}"
        )


if __name__ == "__main__":
    utils.setup_ui()
    Aplicacion().ejecutar()
