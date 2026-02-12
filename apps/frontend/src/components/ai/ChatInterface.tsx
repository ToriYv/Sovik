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

// src/components/ai/ChatInterface.tsx
"use client";

import React, { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { generateComponent } from "@/lib/api";
import { ChatMessage as ChatMessageType } from "@/types";

export const ChatInterface: React.FC = () => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]); // ✅ ИСПРАВЛЕНО: убрана лишняя скобка
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState("idle");

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (userMessage: string) => {
    // Добавляем сообщение пользователя
    const userMsg: ChatMessageType = {
      id: Date.now().toString(),
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(), // ⚠️ Также исправьте на new Date()
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setCurrentStage("analyzing");

    try {
      const response = await generateComponent({ prompt: userMessage });

      if (response.success) {
        const data = response.data;

        // Обработка анализа требований
        if (data.requirements?.key_features) {
          const reqMsg: ChatMessageType = {
            id: `req-${Date.now()}`,
            role: "assistant",
            content: "✅ Анализ требований завершён",
            timestamp: new Date().toISOString(),
            stage: "Анализ требований",
            data: { analysis: data.requirements },
          };
          setMessages((prev) => [...prev, reqMsg]);
        }

        // Обработка дизайна компонента
        if (data.design) {
          const designSpec = {
            name: "ProductCard",
            props: data.design.props || {},
            variants: data.design.variants || [],
            slots: data.design.slots || [],
            tailwind_classes: {}
          };

          const designMsg: ChatMessageType = {
            id: `design-${Date.now()}`,
            role: "assistant",
            content: `🎨 Спецификация компонента "${designSpec.name}" создана`,
            timestamp: new Date().toISOString(),
            stage: "Дизайн компонента",
            data: designSpec,
          };
          setMessages((prev) => [...prev, designMsg]);
        }

        // Обработка кода
        if (data.code?.content) {
          // Извлекаем чистый код из блока ```jsx
          let cleanCode = data.code.content;
          if (cleanCode.startsWith('```')) {
            const lines = cleanCode.split('\n');
            cleanCode = lines.slice(1, -1).join('\n');
          }
          cleanCode = cleanCode.trim();

          // Определяем имя компонента
          let componentName = "Component";
          const match = cleanCode.match(/const\s+(\w+)/);
          if (match) {
            componentName = match[1];
          }

          const codeMsg: ChatMessageType = {
            id: `code-${Date.now()}`,
            role: "assistant",
            content: `✅ Код сгенерирован: ${componentName}`,
            timestamp: new Date().toISOString(),
            stage: "Генерация кода",
            data: {
              content: cleanCode,
              language: data.code.language || "tsx",
              component_name: componentName
            },
          };
          setMessages((prev) => [...prev, codeMsg]);
        }

        // Обработка ревью
        if (data.review) {
          let qualityScore = 7;
          if (data.review.quality === "Excellent" || data.review.quality === "High") {
            qualityScore = 9;
          } else if (data.review.quality === "Good") {
            qualityScore = 8;
          } else if (data.review.quality === "Fair") {
            qualityScore = 6;
          } else if (data.review.quality === "Poor") {
            qualityScore = 4;
          }

          const reviewMsg: ChatMessageType = {
            id: `review-${Date.now()}`,
            role: "assistant",
            content: `🔍 Ревью завершено. Качество: ${qualityScore}/10`,
            timestamp: new Date().toISOString(),
            stage: "Ревью кода",
            data: {
              quality_score: qualityScore,
              ...data.review
            },
          };
          setMessages((prev) => [...prev, reviewMsg]);
        }
      } else {
        const errorMsg: ChatMessageType = {
          id: `error-${Date.now()}`,
          role: "assistant",
          content: `❌ Ошибка: ${response.error || "Не удалось обработать запрос"}`,
          timestamp: new Date().toISOString(),
          stage: "Ошибка",
          data: null,
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    } catch (error: any) {
      const errorMsg: ChatMessageType = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `❌ Ошибка: ${error.message || "Неизвестная ошибка"}`,
        timestamp: new Date().toISOString(),
        stage: "Ошибка",
        data: null,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      setCurrentStage("idle");
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)]">
      {/* История чата */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="text-center py-12 text-neutral-500">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-xl font-bold text-neutral-900 mb-2">
              Добро пожаловать в Local AI Studio!
            </h3>
            <p className="max-w-md mx-auto">
              Напишите, какой компонент вы хотите создать, и я помогу вам его
              спроектировать, сгенерировать и проверить.
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              role={msg.role}
              content={msg.content}
              stage={msg.stage}
              data={msg.data}
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Индикатор загрузки */}
      {isLoading && (
        <div className="px-6 py-3 bg-primary-50 border-t border-primary-200">
          <div className="flex items-center gap-2 text-primary-700 text-sm">
            <div className="animate-pulse">●</div>
            <span>Генерирую компонент... Этап: {currentStage}</span>
          </div>
        </div>
      )}

      {/* Поле ввода */}
      <div className="p-6 border-t border-neutral-200 bg-white">
        <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};