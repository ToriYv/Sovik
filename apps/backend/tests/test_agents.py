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
Интеграционные тесты для всей мультиагентной системы.
Проверяет работу полного воркфлоу от анализа до ревью.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.services.ollama_service import OllamaService
from src.agents.workflow import create_workflow
from src.agents.schemas import AgentState


@pytest.mark.asyncio
async def test_full_workflow_mock():
    """Тест полного воркфлоу с моками."""
    # Создаём комплексный мок для OllamaService
    mock_ollama = AsyncMock()

    # Настройка ответов для разных этапов
    def mock_generate_json(prompt, **kwargs):
        if "анализ" in prompt.lower() or "requirements" in kwargs.get('task_type', ''):
            return {
                "component_type": "Button",
                "purpose": "Интерактивная кнопка",
                "features": ["Текст", "Иконка", "Варианты"],
                "styling_requirements": ["Современный стиль"],
                "technical_requirements": ["React", "TypeScript"],
                "accessibility_notes": ["Поддержка клавиатуры"],
                "dependencies": []
            }
        elif "дизайн" in prompt.lower() or "design" in kwargs.get('task_type', ''):
            return {
                "name": "Button",
                "description": "Интерактивная кнопка",
                "props": {
                    "children": {"type": "ReactNode", "required": "false", "default": "''", "description": "Текст"},
                    "variant": {"type": "'primary'|'secondary'", "required": "false", "default": "'primary'", "description": "Вариант"}
                },
                "variants": {"variant": ["primary", "secondary"], "size": ["sm", "md"]},
                "slots": ["icon", "children"],
                "states": ["idle", "hover", "active", "disabled"],
                "tailwind_classes": {"base": "flex items-center", "variants": {"primary": "bg-blue-600"}},
                "example_usage": "<Button>Click</Button>",
                "architecture_notes": ["Использовать forwardRef"]
            }
        elif "ревью" in prompt.lower() or "review" in kwargs.get('task_type', ''):
            return {
                "quality_score": 8,
                "issues": [],
                "suggestions": ["Добавить больше комментариев"],
                "best_practices_violated": [],
                "security_concerns": [],
                "performance_notes": [],
                "accessibility_issues": [],
                "specification_compliance": "полное соответствие"
            }
        else:  # Генерация кода
            return '''
import React from 'react';

interface ButtonProps {
  children?: React.ReactNode;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ children, variant = 'primary' }) => {
  const baseClasses = 'flex items-center px-4 py-2 rounded font-medium';
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300'
  };

  return (
    <button className={`${baseClasses} ${variantClasses[variant]}`}>
      {children}
    </button>
  );
};

export default Button;
'''

    def mock_generate(prompt, **kwargs):
        if "ревью" in prompt.lower() or "review" in kwargs.get('task_type', ''):
            return "Оценка: 8/10. Код качественный."
        else:
            return mock_generate_json(prompt, **kwargs)

    mock_ollama.generate_json.side_effect = mock_generate_json
    mock_ollama.generate.side_effect = mock_generate

    # Создаём воркфлоу с моком
    workflow = create_workflow(mock_ollama)

    # Запускаем полный воркфлоу
    result = await workflow.run("Создай компонент кнопки с иконкой")

    # Проверяем результат
    assert result["success"] == True
    assert result["errors"] == []

    # Проверяем все этапы
    assert result["requirements"] is not None
    assert result["design"] is not None
    assert result["code"] is not None
    assert result["review"] is not None

    # Проверяем содержимое
    assert result["code"]["component_name"] == "Button"
    assert result["code"]["language"] == "tsx"
    assert len(result["code"]["content"]) > 0
    assert result["review"]["quality_score"] == 8

    # Проверяем количество вызовов
    assert mock_ollama.generate.call_count >= 1
    assert mock_ollama.generate_json.call_count >= 3

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_workflow_error_handling():
    """Тест обработки ошибок в воркфлоу."""
    mock_ollama = AsyncMock()
    mock_ollama.generate.side_effect = Exception("Network error")
    mock_ollama.generate_json.side_effect = Exception("Network error")

    workflow = create_workflow(mock_ollama)

    result = await workflow.run("Создай компонент")

    # Должен вернуть ошибку, но не упасть
    assert result["success"] == False
    assert len(result["errors"]) > 0

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_workflow_improvement_loop():
    """Тест цикла улучшения кода."""
    mock_ollama = AsyncMock()

    call_count = 0
    def mock_generate_json(prompt, **kwargs):
        nonlocal call_count
        call_count += 1

        if "анализ" in prompt.lower():
            return {
                "component_type": "SimpleComponent",
                "purpose": "Простой компонент",
                "features": ["Базовая функциональность"],
                "styling_requirements": ["Простой стиль"],
                "technical_requirements": ["React"],
                "accessibility_notes": [],
                "dependencies": []
            }
        elif "дизайн" in prompt.lower():
            return {
                "name": "SimpleComponent",
                "description": "Простой компонент",
                "props": {"children": {"type": "ReactNode", "required": "false", "default": "''", "description": "Контент"}},
                "variants": {},
                "slots": ["children"],
                "states": ["idle"],
                "tailwind_classes": {"base": "p-4"},
                "example_usage": "<SimpleComponent />",
                "architecture_notes": []
            }
        elif "ревью" in prompt.lower():
            # Первые 2 раза возвращаем низкую оценку, потом высокую
            if call_count <= 2:
                return {
                    "quality_score": 5,
                    "issues": [{"severity": "important", "category": "style", "description": "Нужны комментарии"}],
                    "suggestions": ["Добавить комментарии"],
                    "specification_compliance": "частичное соответствие"
                }
            else:
                return {
                    "quality_score": 8,
                    "issues": [],
                    "suggestions": [],
                    "specification_compliance": "полное соответствие"
                }
        else:  # Генерация кода
            return "const SimpleComponent = () => <div>Simple Component</div>;"

    def mock_generate(prompt, **kwargs):
        if "ревью" in prompt.lower():
            if call_count <= 2:
                return "Оценка: 5/10. Нужны улучшения."
            else:
                return "Оценка: 8/10. Хороший код."
        else:
            return mock_generate_json(prompt, **kwargs)

    mock_ollama.generate_json.side_effect = mock_generate_json
    mock_ollama.generate.side_effect = mock_generate

    workflow = create_workflow(mock_ollama)

    result = await workflow.run("Создай простой компонент")

    # Должен пройти несколько итераций улучшения
    assert result["success"] == True
    assert result["review"]["quality_score"] == 8

    # Проверяем, что было несколько вызовов генерации кода
    code_generation_calls = sum(1 for call in mock_ollama.generate.call_args_list
                              if "ревью" not in str(call))
    assert code_generation_calls >= 2  # Минимум 2 раза: первоначальная + улучшение

    await mock_ollama.close()


@pytest.mark.asyncio
async def test_agent_state_serialization():
    """Тест сериализации состояния агента."""
    state = AgentState(
        user_input="Тестовый запрос",
        requirements_analysis={"component_type": "Test"},
        component_design={"name": "TestComponent"},
        generated_code="console.log('test');",
        code_review={"quality_score": 7}
    )

    # Проверяем, что состояние можно сериализовать в JSON
    state_dict = state.dict()
    assert isinstance(state_dict, dict)
    assert state_dict["user_input"] == "Тестовый запрос"
    assert state_dict["requirements_analysis"]["component_type"] == "Test"
    assert state_dict["component_design"]["name"] == "TestComponent"
    assert state_dict["generated_code"] == "console.log('test');"
    assert state_dict["code_review"]["quality_score"] == 7


if __name__ == "__main__":
    # Запуск тестов вручную
    asyncio.run(test_full_workflow_mock())