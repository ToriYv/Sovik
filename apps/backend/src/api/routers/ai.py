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

# src/api/routers/ai.py
"""
Роутер для работы с мультиагентной системой AI.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback

# ✅ ПРАВИЛЬНЫЕ ИМПОРТЫ (абсолютные пути от корня src/)
from src.services.ollama_service import OllamaService
from src.agents.workflow import create_workflow

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    stream: bool = False

@router.post("/generate")
async def generate_component(request: GenerateRequest):
    try:
        print("🔍 Шаг 1: Создание OllamaService")
        ollama_service = OllamaService()
        print("✅ Шаг 1: Успешно")

        print("🔍 Шаг 2: Создание workflow")
        workflow = create_workflow(ollama_service)
        print("✅ Шаг 2: Успешно")

        print(f"🔍 Шаг 3: Запуск workflow с промптом: {request.prompt[:50]}...")
        result = await workflow.run(request.prompt)
        print("✅ Шаг 3: Успешно")

        await ollama_service.close()
        return {"success": True, "data": result}

    except Exception as e:
        error_msg = f"❌ Критическая ошибка: {str(e)}"
        print(error_msg)
        print("Трейсбек:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)