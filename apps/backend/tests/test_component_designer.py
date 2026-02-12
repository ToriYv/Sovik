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
Тесты для агента дизайнера компонентов.
Проверяет корректность проектирования архитектуры компонентов.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.services.ollama_service import OllamaService
from src.agents.component_designer import create_component_designer
from src.agents.schemas import AgentState


@pytest.mark.asyncio
async def test_component_designer_basic():
    """Тест базовой функциональности дизайнера компонентов."""
    # Создаём мок для OllamaService
    mock_ollama = AsyncMock()
    mock_ollama.generate_json.return_value = {
        "name": "Button",
        "description": "Интерактивная кнопка",
        "props": {
            "children": {
                "type": "ReactNode",
                "required": "false",
                "default": "''",
                "description": "Текст кнопки"
            },
            "variant": {
                "type": "'primary' | 'secondary'",
                "required": "false",
                "default": "'primary'",
                "description": "Вариант кнопки"
            }
        },
        "variants": {
            "variant": ["primary", "secondary"],
            "size": ["sm", "md", "lg"]
        },
        "slots": ["icon", "children"],
        "states": ["idle", "hover", "active", "disabled"],
        "tailwind_classes": {
            "base": "flex items-center justify-center",
            "variants": {
                "primary": "bg-blue-600 text-white"
            },
            "transitions": "transition-all duration-200"
        },
        "example_usage": "<Button>Click me</Button>",
        "architecture_notes": ["Использовать forwardRef"]
    }

    # Создаём дизайнера с моком
    designer = create_component_designer(mock_ollama)

    # Создаём состояние с анализом требований
    state = AgentState(
        user_input="Создай компонент кнопки",
        requirements_analysis={
            "component_type": "Button",
            "purpose": "Интерактивная кнопка для действий",
            "features": ["Отображение текста", "Разные варианты стилей"],
            "styling_requirements": ["Современный дизайн", "Плавные переходы"],
            "technical_requirements": ["React", "TypeScript", "Tailwind CSS"],
            "accessibility_notes": ["Поддержка клавиатуры"],
            "dependencies": []
        },
        requirements_complete=True
    )

    # Запускаем дизайнера
    result = await designer.process(state)

    # Проверяем результат
    assert result.design_complete == True
    assert result.component_design is not None

    design = result.component_design
    assert design["name"] == "Button"
    assert "children" in design["props"]
    assert "variant" in design["props"]
    assert "primary" in design["variants"]["variant"]
    assert "sm" in design["variants"]["size"]
    assert "icon" in design["slots"]

    # Проверяем вызов мока
    mock_ollama.generate_json.assert_called_once()

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_component_designer_fallback():
    """Тест fallback-поведения при ошибке."""
    # Создаём мок, который выбрасывает ошибку
    mock_ollama = AsyncMock()
    mock_ollama.generate_json.side_effect = Exception("Ollama error")

    designer = create_component_designer(mock_ollama)

    state = AgentState(
        user_input="Создай компонент",
        requirements_analysis={
            "component_type": "Card",
            "purpose": "Карточка товара",
            "features": ["Изображение", "Название", "Цена"],
            "styling_requirements": ["Карточный стиль"],
            "technical_requirements": ["React"],
            "accessibility_notes": [],
            "dependencies": []
        },
        requirements_complete=True
    )

    result = await designer.process(state)

    # Должен создать fallback-спецификацию
    assert result.design_complete == True
    assert result.component_design is not None
    assert result.component_design["name"] == "Card"
    assert len(result.errors) > 0

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_component_designer_without_requirements():
    """Тест обработки отсутствия анализа требований."""
    mock_ollama = AsyncMock()
    designer = create_component_designer(mock_ollama)

    state = AgentState(
        user_input="Создай компонент",
        requirements_complete=False
    )

    result = await designer.process(state)

    # Должен завершить дизайн с ошибкой
    assert result.design_complete == True
    assert len(result.errors) > 0

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_integration_with_real_ollama():
    """
    Интеграционный тест с реальным Ollama (опционально).
    Раскомментируйте только если Ollama сервер запущен.
    """
    pytest.skip("Пропущен: требует запущенного Ollama сервера")

    service = OllamaService()
    designer = create_component_designer(service)

    state = AgentState(
        user_input="Создай простую кнопку",
        requirements_analysis={
            "component_type": "Button",
            "purpose": "Простая кнопка",
            "features": ["Текст"],
            "styling_requirements": ["Базовый стиль"],
            "technical_requirements": ["React"],
            "accessibility_notes": [],
            "dependencies": []
        },
        requirements_complete=True
    )

    result = await designer.process(state)

    assert result.design_complete == True
    assert result.component_design is not None
    assert "name" in result.component_design
    assert "props" in result.component_design

    await service.close()


def test_get_component_name():
    """Тест метода получения названия компонента."""
    from src.agents.component_designer import ComponentDesignerAgent

    # Создаём мок сервиса
    mock_service = AsyncMock()
    designer = ComponentDesignerAgent(mock_service)

    # Тест с существующей спецификацией
    state_with_design = AgentState(
        component_design={"name": "CustomButton"},
        design_complete=True
    )

    # Тест с отсутствующей спецификацией
    state_without_design = AgentState(
        design_complete=False
    )

    # Проверяем получение названия
    name1 = asyncio.run(designer.get_component_name(state_with_design))
    name2 = asyncio.run(designer.get_component_name(state_without_design))

    assert name1 == "CustomButton"
    assert name2 == "Component"


if __name__ == "__main__":
    # Запуск тестов вручную
    asyncio.run(test_component_designer_basic())