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
        self.df_crudo = None
        self.df_procesado = None
        self.rango_valido = (1, 50)

    def cargar_datos(self, df: Optional[DataFrame]):
        """Carga y procesa los datos de entrada

        Args:
            df (Optional[pd.DataFrame]): DataFrame con datos crudos
        """
        if df is not None and not df.empty:
            add_key_ss_st(clave="df_insumo", valor_inicial=df)
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