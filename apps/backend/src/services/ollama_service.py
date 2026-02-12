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
Ollama Service - централизованный сервис для работы с LLM через Ollama.
Поддерживает переключение моделей в зависимости от типа задачи.
Оптимизирован для работы с 8 ГБ ОЗУ (только одна модель в памяти).
"""

import httpx
import json
import logging
from typing import AsyncGenerator, List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskType(str, Enum):
    """Типы задач для автоматического переключения моделей"""
    REQUIREMENTS_ANALYSIS = "requirements_analysis"  # Анализ требований (русский)
    COMPONENT_DESIGN = "component_design"            # Дизайн компонентов
    CODE_GENERATION = "code_generation"              # Генерация кода
    CODE_REVIEW = "code_review"                     # Ревью кода


class OllamaConfig(BaseModel):
    """Конфигурация подключения к Ollama"""
    base_url: str = Field(default="http://localhost:11434")
    model_default: str = Field(default="qwen2.5-coder:3b")  # Для кода
    model_russian: str = Field(default="qwen2.5:3b")       # Для русского
    model_embedding: str = Field(default="nomic-embed-text")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    timeout: int = Field(default=120)


class OllamaService:
    """
    Сервис для взаимодействия с Ollama API.
    Особенности:
    - Автоматическое переключение моделей по типу задачи
    - Поддержка стриминга ответов
    - Обработка ошибок и логирование
    """

    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self.client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout
        )
        logger.info(f"OllamaService инициализирован. URL: {self.config.base_url}")

    def _get_model_for_task(self, task_type: TaskType) -> str:
        """Определяет модель для конкретной задачи."""
        model_mapping = {
            TaskType.REQUIREMENTS_ANALYSIS: self.config.model_russian,      # qwen2.5:3b - лучше понимает русский
            TaskType.COMPONENT_DESIGN: self.config.model_default,           # qwen2.5-coder:3b - дизайн компонентов
            TaskType.CODE_GENERATION: self.config.model_default,            # qwen2.5-coder:3b - генерация кода
            TaskType.CODE_REVIEW: self.config.model_default,                # qwen2.5-coder:3b - ревью кода
        }
        return model_mapping.get(task_type, self.config.model_default)

    async def generate(
        self,
        prompt: str,
        task_type: TaskType = TaskType.CODE_GENERATION,
        system_prompt: Optional[str] = None
    ) -> str:
        """Генерация текста через Ollama (блокирующий режим)."""
        model = self._get_model_for_task(task_type)
        logger.info(f"Генерация. Модель: {model}, Тип: {task_type.value}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            }
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]

        except Exception as e:
            logger.error(f"Ошибка Ollama: {e}")
            raise Exception(f"Ollama error: {e}")

    async def generate_json(
        self,
        prompt: str,
        task_type: TaskType = TaskType.CODE_GENERATION,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Генерация структурированных данных в формате JSON."""
        json_instruction = """
Отвечай строго в формате JSON. Не добавляй пояснений, только валидный JSON.
"""
        combined_system_prompt = system_prompt + json_instruction if system_prompt else json_instruction

        try:
            response = await self.generate(
                prompt=prompt,
                task_type=task_type,
                system_prompt=combined_system_prompt
            )

            # Очищаем и парсим JSON
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response[3:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]

            return json.loads(cleaned_response)

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {"error": "Failed to parse JSON", "raw_response": response}

    async def close(self):
        """Закрытие соединения."""
        await self.client.aclose()
        logger.info("OllamaService закрыт")