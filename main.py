from pandas import DataFrame
import streamlit as st
from ui_components.ui_components import ButtonTracker, add_key_ss_st, clean_key_ss_st, set_key_ss_st
import ui_components.utils as utils
from Controllers.sidebar_controller import ControladorBarraLateral
from Controllers.main_content_controller import GestorContenidoPrincipal
from services.data_service import GestorDatos
from config_loader import ConfigLoader


class Aplicacion:
    """Clase principal que controla el flujo de la aplicación"""

    def __init__(self):
        self.cargador_config = ConfigLoader(utils=utils)

        self.barra_lateral = ControladorBarraLateral(
            config_lv=self.cargador_config.cnf_lateral_var
        )

        self.gestor_datos = GestorDatos(self.cargador_config)

        self.contenido_principal = GestorContenidoPrincipal(self.gestor_datos)

    def ejecutar(self):
        """Método principal que ejecuta la aplicación"""
        add_key_ss_st("list_materiales", valor_inicial=[])
        add_key_ss_st("registro_confirmado", valor_inicial=False)
        add_key_ss_st("confirmar_edicion_pendiente", valor_inicial=False)

        rango_act, portje_cremto_act, df_insumo = (
            self.barra_lateral.controlador_barra_lateral()
        )

        self.gestor_datos.validar_rango(rango_act)
        self.gestor_datos.cargar_datos(df_insumo)
        df_procesado_insumo = self.gestor_datos.df_procesado

        boton_agregar_material = ButtonTracker(
            clave="Agregar_mat", etiqueta="Agregar material", usar_sidebar=True
        )

        boton_confirmar_registro = ButtonTracker(
            clave="confirmar_registro",
            etiqueta="✅ Confirmar registro",
            usar_sidebar=False,
            auto_render=False,
        )
        if df_procesado_insumo is not None and boton_agregar_material.fue_presionado():
            set_key_ss_st("registro_confirmado", False)
            set_key_ss_st("edicion_confirmada", False)
            set_key_ss_st("confirmar_edicion_pendiente", False)

            dict_final = self.contenido_principal.ejecutar_contenido_principal()

            claves_a_conservar = {
                "selector_rango_dcto",
                "df_insumo",
                "df_final",
                "text_input_crecimiento_valido",
                "btn_confirmar_rango_estado",
                "portje_cremto_act",
                "btn_confirmar_%_crecimiento_widget",
                "btn_confirmar_%_crecimiento_estado",
                "archivo_excel",
                "btn_confirmar_rango_widget",
                "rango_act",
                "text_input_crecimiento",
                "list_materiales",
                "registro_confirmado",
                "confirmar_edicion_pendiente",
            }

            boton_confirmar_registro._mostrar_boton()
            if boton_confirmar_registro.fue_presionado():
                dict_final_aplanado = utils.aplanar_diccionario(
                    dict_final, clave_aplanar="Fecha"
                )

                st.session_state["list_materiales"].append(dict_final_aplanado)

                df_para_calculos = DataFrame(st.session_state["list_materiales"])

                claves_a_eliminar = [
                    clave
                    for clave in st.session_state.keys()
                    if clave not in claves_a_conservar
                ]

                clean_key_ss_st(keys=claves_a_eliminar)

                set_key_ss_st("df_final", df_para_calculos)
                set_key_ss_st("registro_confirmado", True)
                st.success("✅ Registro confirmado. Ahora puedes editar los datos.")
                st.rerun()

        if "df_final" in st.session_state and st.session_state["registro_confirmado"]:
            st.subheader("✏️ Editar datos registrados")

            # Copia y añade columna de control
            df_edicion = st.session_state["df_final"].copy()
            df_edicion["Eliminar"] = False  # Columna auxiliar

            df_editado = st.data_editor(
                df_edicion,
                key="editor_df_final",
                use_container_width=True,
                disabled=["concat_plu_producto"],
                num_rows="fixed",
            )

            # Activar bandera si se presionó el botón
            if st.button("💾 Confirmar edición"):
                st.session_state["confirmar_edicion_pendiente"] = True
                set_key_ss_st("list_materiales", df_editado.to_dict(orient="records"))
                st.rerun()

                # Eliminar filas seleccionadas
            if st.button("🗑️ Eliminar filas seleccionadas"):
                df_filtrado = df_editado[df_editado["Eliminar"] == False].drop(
                    columns=["Eliminar"]
                )
                set_key_ss_st("df_final", df_filtrado)
                set_key_ss_st("list_materiales", df_filtrado.to_dict(orient="records"))
                st.success("✅ Filas eliminadas correctamente.")
                st.rerun()

            # Aplicar edición si la bandera fue activada
            if st.session_state["confirmar_edicion_pendiente"]:
                set_key_ss_st("df_final", df_editado)
                st.success("✅ Edición confirmada.")
                set_key_ss_st("edicion_confirmada", True)
                st.session_state["confirmar_edicion_pendiente"] = False
                st.rerun()

        if "df_final" in st.session_state and st.session_state.get(
            "edicion_confirmada", False
        ):
            df_merge = utils.left_merge_on_columns(
                df1=st.session_state["df_final"],
                df2=df_procesado_insumo[
                    [
                        "concat_plu_producto",
                        "plu",
                        "producto",
                        "Venta $$ Promedio Mes",
                        "Promedio Mes Und",
                        "Precio de venta",
                    ]
                ],
                key_columns=["concat_plu_producto"],
            )

            df_procesado_final = utils.procesar_insumo(
                df_insumo=df_merge,
                porcentaje_crecimiento=portje_cremto_act,
                dict_cols=self.cargador_config.config["df_insumo"]["dict_cols"],
            )

            set_key_ss_st("df_procesado_final", df_procesado_final)
            st.dataframe(df_procesado_final, use_container_width=True)

            st.markdown("### Promedios actuales:")
            promedios = (
                df_procesado_final[["Venta de la actividad", "Costo del descuento"]]
                .mean()
                .round(2)
            )
            set_key_ss_st("promedios", promedios)

            col1, col2 = st.columns(2)
            col1.metric(
                "🧾 Prom. Venta de la actividad",
                f"${promedios['Venta de la actividad']:,}",
            )
            col2.metric(
                "💸 Prom. Costo del descuento", f"${promedios['Costo del descuento']:,}"
            )

        elif df_procesado_insumo is None:
            st.warning("⚠️ Aún no se ha cargado un archivo de insumos.")
            st.stop()


if __name__ == "__main__":
    utils.setup_ui()
    Aplicacion().ejecutar()
