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
Агент генератора кода.
Создаёт функциональный код компонентов на основе анализа требований.
"""

from .base import BaseAgent
from .schemas import AgentState
from .prompts import CODE_GENERATOR_SYSTEM_PROMPT
from ..services.ollama_service import TaskType

class CodeGeneratorAgent(BaseAgent):
    """Агент для генерации кода компонентов."""

    def __init__(self, ollama_service):
        super().__init__(
            ollama_service=ollama_service,
            name="code_generator",
            task_type=TaskType.CODE_GENERATION,
            system_prompt=CODE_GENERATOR_SYSTEM_PROMPT
        )

    async def process(self, state: AgentState) -> AgentState:
        """Процесс генерации кода."""
        try:
            design_context = state.component_design or state.requirements_analysis
            prompt = f"Сгенерируй код на основе: {design_context}"
            code = await self._generate_response(prompt)

            state.generated_code = code
            state.code_language = "tsx"
            state.code_generated = True
            state.iteration_count += 1

        except Exception as e:
            state.errors.append(f"Ошибка генератора: {e}")
            state.code_generated = True

        return state

def create_code_generator(ollama_service):
    return CodeGeneratorAgent(ollama_service)