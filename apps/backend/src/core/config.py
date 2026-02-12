# Copyright 2026 ToriYv, SofochkaSofia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Конфигурация приложения с использованием Pydantic Settings.
Позволяет загружать настройки из переменных окружения и .env файла.
"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Ollama settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL_DEFAULT: str = "qwen2.5-coder:3b"  # Для кода
    OLLAMA_MODEL_RUSSIAN: str = "qwen2.5:3b"       # Для русского языка
    OLLAMA_MODEL_EMBEDDING: str = "nomic-embed-text"

    # Model parameters
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2000

    # Database
    DATABASE_URL: str = "postgresql://ai_user:ai_password@localhost:5432/ai_studio"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()