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
Агент ревьюера кода.
Анализирует сгенерированный код и выявляет проблемы.
"""

from .base import BaseAgent
from .schemas import AgentState
from .prompts import CODE_REVIEWER_SYSTEM_PROMPT
from ..services.ollama_service import TaskType

class CodeReviewerAgent(BaseAgent):
    """Агент для ревью кода."""

    def __init__(self, ollama_service):
        super().__init__(
            ollama_service=ollama_service,
            name="code_reviewer",
            task_type=TaskType.CODE_REVIEW,
            system_prompt=CODE_REVIEWER_SYSTEM_PROMPT
        )

    async def process(self, state: AgentState) -> AgentState:
        """Процесс ревью кода."""
        try:
            if not state.generated_code:
                raise ValueError("Нет сгенерированного кода")

            prompt = f"Проведи ревью кода: {state.generated_code}"
            review = await self._generate_response(prompt, return_json=True)

            state.code_review = review
            state.code_reviewed = True
            state.iteration_count += 1

        except Exception as e:
            state.errors.append(f"Ошибка ревьюера: {e}")
            state.code_reviewed = True

        return state

    def get_quality_score(self, state: AgentState) -> int:
        """Получает оценку качества из результатов ревью."""
        if state.code_review:
            return state.code_review.get('quality_score', 0)
        return 0

def create_code_reviewer(ollama_service):
    return CodeReviewerAgent(ollama_service)