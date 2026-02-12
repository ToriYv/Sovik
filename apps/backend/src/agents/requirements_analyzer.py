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
Агент анализатора требований.
Анализирует пользовательский запрос и выделяет ключевые требования.
"""

from .base import BaseAgent
from .schemas import AgentState
from .prompts import REQUIREMENTS_ANALYZER_SYSTEM_PROMPT
from ..services.ollama_service import TaskType
from typing import Any

class RequirementsAnalyzerAgent(BaseAgent):
    """Агент для анализа требований к компонентам."""

    def __init__(self, ollama_service):
        super().__init__(
            ollama_service=ollama_service,
            name="requirements_analyzer",
            task_type=TaskType.REQUIREMENTS_ANALYSIS,
            system_prompt=REQUIREMENTS_ANALYZER_SYSTEM_PROMPT
        )

    async def process(self, state: AgentState) -> AgentState:
        """Процесс анализа требований."""
        try:
            prompt = f"Проанализируй запрос: {state.user_input}"
            analysis_text = await self._generate_response(prompt)
            analysis_json = await self._generate_response(
                f"Создай JSON из анализа: {analysis_text}",
                return_json=True
            )

            state.requirements = analysis_text
            state.requirements_analysis = analysis_json
            state.requirements_complete = True
            state.iteration_count += 1

        except Exception as e:
            state.errors.append(f"Ошибка анализатора: {e}")
            state.requirements_complete = True

        return state

def create_requirements_analyzer(ollama_service):
    return RequirementsAnalyzerAgent(ollama_service)