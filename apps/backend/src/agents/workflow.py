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
Основной граф работы мультиагентной системы.
"""

import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END

from .schemas import AgentState
from .requirements_analyzer import create_requirements_analyzer
from .component_designer import create_component_designer
from .code_generator import create_code_generator
from .code_reviewer import create_code_reviewer

logger = logging.getLogger(__name__)


class MultiAgentWorkflow:
    """
    Мультиагентный воркфлоу на базе LangGraph.
    """

    def __init__(self, ollama_service):
        self.ollama_service = ollama_service

        # Создаём агентов
        self.requirements_analyzer = create_requirements_analyzer(ollama_service)
        self.component_designer = create_component_designer(ollama_service)
        self.code_generator = create_code_generator(ollama_service)
        self.code_reviewer = create_code_reviewer(ollama_service)

        # Создаём граф
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Строит граф состояний и переходов."""
        # Определяем структуру состояния как dict (не Pydantic модель!)
        workflow = StateGraph(dict)

        workflow.add_node("analyze_requirements", self._analyze_requirements_node)
        workflow.add_node("design_component", self._design_component_node)
        workflow.add_node("generate_code", self._generate_code_node)
        workflow.add_node("review_code", self._review_code_node)

        workflow.set_entry_point("analyze_requirements")
        workflow.add_edge("analyze_requirements", "design_component")
        workflow.add_edge("design_component", "generate_code")
        workflow.add_edge("generate_code", "review_code")

        workflow.add_conditional_edges(
            "review_code",
            self._should_improve_code,
            {"improve": "generate_code", "end": END}
        )

        return workflow.compile()

    async def _analyze_requirements_node(self, state: dict) -> dict:
        """Узел анализа требований."""
        logger.info("Workflow: запуск анализатора требований")
        # Преобразуем dict → AgentState
        agent_state = AgentState(**state)
        # Обрабатываем
        result_state = await self.requirements_analyzer.process(agent_state)
        # Возвращаем dict
        return result_state.dict()

    async def _design_component_node(self, state: dict) -> dict:
        """Узел дизайна компонента."""
        logger.info("Workflow: запуск дизайнера компонентов")
        agent_state = AgentState(**state)
        result_state = await self.component_designer.process(agent_state)
        return result_state.dict()

    async def _generate_code_node(self, state: dict) -> dict:
        """Узел генерации кода."""
        logger.info("Workflow: запуск генератора кода")
        agent_state = AgentState(**state)
        result_state = await self.code_generator.process(agent_state)
        return result_state.dict()

    async def _review_code_node(self, state: dict) -> dict:
        """Узел ревью кода."""
        logger.info("Workflow: запуск ревьюера кода")
        agent_state = AgentState(**state)
        result_state = await self.code_reviewer.process(agent_state)
        return result_state.dict()

    def _should_improve_code(self, state: dict) -> Literal["improve", "end"]:
        """Условие для улучшения кода."""
        # Преобразуем dict → AgentState для удобства
        agent_state = AgentState(**state)

        if agent_state.iteration_count >= 3:
            return "end"

        # Получаем оценку качества
        quality_score = 0
        if agent_state.code_review and isinstance(agent_state.code_review, dict):
            quality_score = agent_state.code_review.get('quality_score', 0)

        if quality_score < 7:
            return "improve"
        return "end"

    async def run(self, user_input: str):
        """Запуск полного воркфлоу."""
        logger.info(f"Workflow: запуск обработки запроса: '{user_input[:50]}...'")

        try:
            # Создаём начальное состояние как dict
            initial_state = AgentState(user_input=user_input)
            initial_dict = initial_state.dict()

            # Запускаем граф
            final_dict = await self.graph.ainvoke(initial_dict)

            # Преобразуем обратно в AgentState для форматирования
            final_state = AgentState(**final_dict)

            return self._format_result(final_state)

        except Exception as e:
            logger.error(f"Workflow: ошибка выполнения - {e}")
            raise

    def _format_result(self, state: AgentState) -> Dict[str, Any]:
        """Форматирует результат для API."""
        return {
            "success": len(state.errors) == 0,
            "errors": state.errors,
            "requirements": state.requirements_analysis if state.requirements_complete else None,
            "design": state.component_design if state.design_complete else None,
            "code": {
                "content": state.generated_code,
                "language": state.code_language,
                "component_name": state.component_name
            } if state.code_generated else None,
            "review": state.code_review if state.code_reviewed else None,
            "iteration_count": state.iteration_count,
            "timestamp": state.timestamp.isoformat() if hasattr(state.timestamp, 'isoformat') else str(state.timestamp)
        }


def create_workflow(ollama_service):
    """Фабричная функция для создания воркфлоу"""
    return MultiAgentWorkflow(ollama_service)