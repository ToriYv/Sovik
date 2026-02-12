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
Агент дизайнера компонентов.
Создаёт детальную спецификацию архитектуры компонента.
"""

from .base import BaseAgent
from .schemas import AgentState
from .prompts import COMPONENT_DESIGNER_SYSTEM_PROMPT
from ..services.ollama_service import TaskType

class ComponentDesignerAgent(BaseAgent):
    """Агент для проектирования архитектуры компонентов."""

    def __init__(self, ollama_service):
        super().__init__(
            ollama_service=ollama_service,
            name="component_designer",
            task_type=TaskType.COMPONENT_DESIGN,
            system_prompt=COMPONENT_DESIGNER_SYSTEM_PROMPT
        )

    async def process(self, state: AgentState) -> AgentState:
        """Процесс проектирования компонента."""
        try:
            if not state.requirements_analysis:
                raise ValueError("Нет анализа требований")

            prompt = f"Спроектируй компонент на основе: {state.requirements_analysis}"
            design_spec = await self._generate_response(prompt, return_json=True)

            state.component_design = design_spec
            state.design_complete = True
            state.iteration_count += 1

        except Exception as e:
            state.errors.append(f"Ошибка дизайнера: {e}")
            state.design_complete = True

        return state

def create_component_designer(ollama_service):
    return ComponentDesignerAgent(ollama_service)