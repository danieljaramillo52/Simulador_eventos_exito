import pandas as pd
from pandas import DataFrame
from typing import Optional
from config_loader import ConfigLoader
from ui_components.ui_components import add_key_ss_st
import ui_components.utils as utils


class GestorDatos:
    """Clase para manejar toda la lógica relacionada con datos"""

    def __init__(self, config_loader: ConfigLoader):
        """
        Args:
            config_loader (ConfigLoader): Instancia de cargador de configuración
        """
        self.config = config_loader.config
        self.df_copy = None
        self.df_procesado = None
        self.df_prec_copy = None
        self.df_vtas_copy = None
        self.df_prec_vtas_procesado = None
        self.rango_valido = (1, 50)

    def procesar_dfs_insumos(
        self,
        df_precios: Optional[pd.DataFrame],
        df_vtas: Optional[pd.DataFrame],
    ):
        """Carga y procesa los datos de entrada

        Args:
            df (Optional[pd.DataFrame]): DataFrame con datos crudos
        """
        # Filtrar solo los años 2024 y 2025

        if df_precios is not None and not df_precios.empty:
            #add_key_ss_st(clave="df_insumo", valor_inicial=df)
            add_key_ss_st(clave="df_precios", valor_inicial=df_precios)
            add_key_ss_st(clave="df_vtas", valor_inicial=df_vtas)

            #self.df_copy = df.copy()
            self.df_prec_copy = df_precios.copy()
            self.df_vtas_copy = df_vtas.copy()

            self._procesar_datos()
            self._procesar_dfs_vtas_y_precios()

    def _procesar_dfs_vtas_y_precios(self):
        """Tranformaciones necesarias sobre la el dataframe de vtas"""
        df_fil_an = utils.filtrar_por_valores(
            df=self.df_vtas_copy, columna="Año", valores=["2024", "2025"]
        )

        # Filtrar Fabricante distinto de "Otros Oper Cciales"
        df_fil_final = utils.filtrar_por_valores(
            df=df_fil_an,
            columna="Fabricante",
            valores=["Otros Oper Cciales"],
            incluir=False,
        )

        df_fil_final = utils.Cambiar_tipo_dato_multiples_columnas_pd(
            base=df_fil_final, list_columns=["Ventas_COP", "Ventas_Un"], type_data=float
        )
        # Tramiento básico nulos previo a agrupación.
        df_fil_final = df_fil_final.fillna("-")

        # Agrupar y sacar promedio
        group_cols = [
            "Agrupación Formatos",
            "Marca",
            "Cod. SAP Unificado",
            "PLU",
            "EAN Unificado",
            "Fabricante",
            "Categoría",
            "Subcategoría",
            "Producto Unificado",
        ]
        dict_sap_ean_diferentes = {
            k: v
            for k, v in zip(
                df_fil_final["EAN Unificado"], df_fil_final["Cod. SAP Unificado"]
            )
            if k != v
        }

        df_fil_final = utils.reemplazar_columna_en_funcion_de_otra(
            df_fil_final,
            nom_columna_a_reemplazar="Cod. SAP Unificado",
            nom_columna_de_referencia="EAN Unificado",
            mapeo=dict_sap_ean_diferentes,
        )

        df_fil_final_group = utils.group_by_and_operate(
            df=df_fil_final,
            group_col=group_cols,
            operation_cols=["Ventas_COP", "Ventas_Un"],
            operation="mean",
        )

        df_fil_final_group = utils.left_merge_on_columns(
            df1=df_fil_final_group,
            df2=self.df_prec_copy[
                ["PLU", "SUBLINEA", "P. LISTA CON IVA", "P. SUGERIDO"]
            ],
            key_columns=["PLU"],
        )
        df_fil_final_group[["P. LISTA CON IVA", "P. SUGERIDO"]] = df_fil_final_group[
            ["P. LISTA CON IVA", "P. SUGERIDO"]
        ].fillna(0)

        df_fil_final_group_re = utils.renombrar_columnas_con_diccionario(
            df=df_fil_final_group,
            cols_to_rename={
                "Ventas_COP": "Venta $$ Promedio Mes",
                "Ventas_Un": "Promedio Mes Und",
                "Producto Unificado": "producto",
                "P. SUGERIDO": "Precio de venta",
                "SUBLINEA": "Sub",
                "PLU": "plu",
            },
        )

        self.df_prec_vtas_procesado  = utils.concatenar_columnas_pd(
            dataframe=df_fil_final_group_re,
            cols_elegidas=["plu", "producto"],
            nueva_columna="concat_plu_producto",
            usar_separador=True,
            separador=" : ",
        )

    def _procesar_datos(self):
        """Realiza transformaciones básicas en los datos"""
        self.df_procesado = utils.concatenar_columnas_pd(
            dataframe=self.df_copy,
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
