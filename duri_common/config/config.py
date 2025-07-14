import os

class Config:
    def __init__(self):
        self.log_level = os.getenv("DURI_LOG_LEVEL", "INFO")
        self.log_dir = os.getenv("DURI_LOG_DIR", "./logs")
        self.receive_json_log = os.getenv("RECEIVE_JSON_LOG", "./brain_state/receive_log.json")  # ✅ 수정됨
        self.evolution_log = os.getenv("EVOLUTION_LOG_PATH", "./brain_state/receive_log.json")

        self.brain_url = os.getenv("BRAIN_URL", "http://localhost:8081/brain")
        self.evolution_url = os.getenv("EVOLUTION_URL", "http://localhost:8082/evolve")
        self.database_url = os.getenv("DATABASE_URL", "postgresql://duri:duri@localhost:5432/duri")
        self.action_stats_path = os.getenv("ACTION_STATS_PATH", "./brain_state/action_stats.json")
        self.port = int(os.getenv("PORT", "8080")) 


    def get_log_level(self) -> str:
        return self.log_level

    def get_log_dir(self) -> str:
        return self.log_dir

    def get_receive_json_log(self) -> bool:
        return self.receive_json_log

    def get_evolution_log(self) -> str:
        return self.evolution_log

    def get_brain_url(self) -> str:
        return self.brain_url

    def get_evolution_url(self) -> str:
        return self.evolution_url

    def get_database_url(self) -> str:
        return self.database_url

    def get_action_stats_path(self) -> str:
        return self.action_stats_path

    def get_port(self) -> int:
        return self.port
