class ConfigLoader:
    """
    Clase responsable de cargar la configuración inicial y los datos necesarios para la aplicación.

    Args:
        utils (module): Módulo con funciones auxiliares como procesar_configuracion
        config_file (str): Ruta al archivo de configuración interno (por defecto: "Core/config.yml")
        editable_file (str): Ruta al archivo de configuración editable por el usuario (por defecto: "Editable.yml")
    """

    def __init__(
        self, utils, config_file="Controllers/Core/config.yml", editable_file="editable.yml"
    ):
        self.utils = utils

        # Cargar configuración protegida e interna
        self.config_interna = self.utils.procesar_configuracion(config_file)

        # Cargar configuración editable del usuario
        self.config_usuario = self._cargar_config_usuario(editable_file)

        # Combinar: lo editable sobreescribe lo interno si hay conflictos
        self.config = self._combinar_configuraciones()

        # Cargar secciones
        self._cargar_configuracion_base()
        self._cargar_nuevas_secciones()

    def _cargar_config_usuario(self, path):
        try:
            return self.utils.procesar_configuracion(path)
        except FileNotFoundError:
            print(
                f"Advertencia: No se encontró el archivo de configuración editable en {path}. Se continuará sin él."
            )
            return {}

    def _combinar_configuraciones(self):
        config_comb = self.config_interna.copy()
        config_comb.update(self.config_usuario)
        return config_comb

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
