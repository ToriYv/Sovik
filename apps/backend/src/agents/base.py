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
Базовый класс для всех агентов.
Предоставляет общую функциональность и интеграцию с OllamaService.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

from ..services.ollama_service import OllamaService, TaskType
from .schemas import AgentState

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Абстрактный базовый класс для всех агентов.
    """

    def __init__(
        self,
        ollama_service: OllamaService,
        name: str,
        task_type: TaskType,
        system_prompt: str
    ):
        self.ollama_service = ollama_service
        self.name = name
        self.task_type = task_type
        self.system_prompt = system_prompt
        logger.info(f"Агент '{self.name}' инициализирован")

    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        """Основной метод обработки состояния агентом."""
        raise NotImplementedError()

    async def _generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        return_json: bool = False
    ) -> Any:
        """Вспомогательный метод для генерации ответа через Ollama."""
        try:
            if return_json:
                result = await self.ollama_service.generate_json(
                    prompt=prompt,
                    task_type=self.task_type,
                    system_prompt=system_prompt or self.system_prompt
                )
            else:
                result = await self.ollama_service.generate(
                    prompt=prompt,
                    task_type=self.task_type,
                    system_prompt=system_prompt or self.system_prompt
                )
            return result
        except Exception as e:
            logger.error(f"Агент '{self.name}': ошибка генерации - {e}")
            raise