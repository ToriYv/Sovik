/*
 * Copyright 2026 ToriYv, SofochkaSofia
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// src/components/ai/ChatInput.tsx
"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Send, Sparkles, Paperclip } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
}) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Опишите компонент, который хотите создать…"
            disabled={isLoading}
            // ✅ ТЕМНЫЙ ТЕКСТ: text-neutral-900 (уже есть)
            // ✅ ЧЕТКИЙ ПЛЕЙСХОЛДЕР: text-neutral-500 → text-neutral-600
            className="w-full px-4 py-3 pr-12 rounded-lg border border-neutral-300 bg-white text-neutral-900 placeholder:text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none min-h-[56px] max-h-[160px]"
            rows={1}
          />
          <div className="absolute right-3 bottom-3 flex gap-1">
            <button
              type="button"
              className="p-1.5 text-neutral-500 hover:text-neutral-700"
              title="Прикрепить файл"
              disabled
            >
              <Paperclip className="h-4 w-4" />
            </button>
          </div>
        </div>

        <Button
          type="submit"
          size="lg"
          disabled={!input.trim() || isLoading}
          className="h-12"
        >
          {isLoading ? (
            <span className="flex items-center">
              <svg
                className="animate-spin h-4 w-4 mr-2 text-white" // ✅ Белый цвет для спиннера
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Генерирую...
            </span>
          ) : (
            <Send className="h-5 w-5" />
          )}
        </Button>

        <Button
          type="button"
          variant="outline"
          size="lg"
          className="h-12"
          onClick={() => {
            const examples = [
              "Создай компонент Header с логотипом, навигацией и кнопкой 'Связаться'",
              "Сделай карточку товара с изображением, названием, ценой и кнопкой 'В корзину'",
              "Создай форму входа с полями логин, пароль и кнопкой 'Войти'",
              "Создай кнопку с иконкой, которая меняет цвет при наведении",
            ];
            setInput(examples[Math.floor(Math.random() * examples.length)]);
          }}
          title="Случайный пример"
        >
          <Sparkles className="h-5 w-5" />
        </Button>
      </div>

      {/* ✅ УЛУЧШЕННЫЙ ПОДСКАЗКА: темнее и понятнее */}
      <div className="mt-2 text-xs text-neutral-600">
        💡 Примеры: «Кнопка с иконкой», «Карточка товара», «Форма регистрации»
      </div>
    </form>
  );
};