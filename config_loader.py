class ConfigLoader:
    """
    Clase responsable de cargar la configuración inicial y los datos necesarios para la aplicación.

    Args:
        utils (module): Módulo que contiene funciones auxiliares como `fetch_data_from_url` y `json_a_dataframe`.
        config_file (str): Ruta al archivo de configuración (por defecto, "config.yml").
    """

    def __init__(self, utils, config_file="config.yml"):
        """
        Inicializa la clase cargando la configuración y preparando los datos iniciales.

        Args:
            utils (module): Módulo con funciones auxiliares.
            config_file (str): Ruta al archivo de configuración.
        """
        self.utils = utils
        self.config = self.utils.procesar_configuracion(
            nom_archivo_configuracion=config_file
        )

        # Cargar valores de config en atributos
        self.cnf_lateral_var = self.config["lateral_var"]
        self.dict_cols = self.config["df_insumo"]["dict_cols"]
        self.cols_df_insumo = self.config["df_insumo"]["cols_select"]
        self.cnf_session_stt = self.config["config_session_state"]["claves_a_conservar"]
        self.textos = self.config["textos"]  # Cargar textos





