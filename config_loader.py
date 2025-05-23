class ConfigLoader:
    """
    Clase responsable de cargar la configuración inicial y los datos necesarios para la aplicación.

    Args:
        utils (module): Módulo con funciones auxiliares como procesar_configuracion
        config_file (str): Ruta al archivo de configuración (default: "config.yml")
    """

    def __init__(self, utils, config_file="config.yml"):
        self.utils = utils
        self.config = self.utils.procesar_configuracion(config_file)
        
        # Cargar todas las secciones de configuración
        self._cargar_configuracion_base()
        self._cargar_nuevas_secciones()

    def _cargar_configuracion_base(self):
        """Carga secciones originales del config para mantener compatibilidad"""
        self.cnf_lateral_var = self.config["lateral_var"]
        self.dict_cols = self.config["df_insumo"]["dict_cols"]
        self.cols_df_insumo = self.config["df_insumo"]["cols_select"]

    def _cargar_nuevas_secciones(self):
        """Carga nuevas secciones para funcionalidades extendidas"""
        self.cnf_session_keys = self.config.get("cnf_session_keys", {})
        self.cnf_botones = self.config.get("cnf_botones", {})
        self.cnf_mensajes = self.config.get("cnf_mensajes", {})
        self.cnf_columnas_data = self.config.get("cnf_columnas_data", {})


