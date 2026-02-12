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
Схемы состояний для мультиагентной системы.
Определяют структуру данных, передаваемых между агентами.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AgentState(BaseModel):
    """Основное состояние агента - передаётся между всеми агентами."""
    user_input: str = Field(..., description="Исходный запрос пользователя")
    current_stage: str = Field(default="requirements_analysis")

    # Анализ требований
    requirements: Optional[str] = Field(None)
    requirements_analysis: Optional[Dict[str, Any]] = Field(None)
    requirements_complete: bool = Field(default=False)

    # Дизайн компонента
    component_design: Optional[Dict[str, Any]] = Field(None)
    design_complete: bool = Field(default=False)

    # Сгенерированный код
    generated_code: Optional[str] = Field(None)
    code_language: Optional[str] = Field(None)
    component_name: Optional[str] = Field(None)
    code_generated: bool = Field(default=False)

    # Ревью кода
    code_review: Optional[Dict[str, Any]] = Field(None)
    issues_found: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    code_reviewed: bool = Field(default=False)

    # Контекст
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)

    # Метаданные
    timestamp: datetime = Field(default_factory=datetime.now)
    iteration_count: int = Field(default=0)
    errors: List[str] = Field(default_factory=list)
    final_output_ready: bool = Field(default=False)