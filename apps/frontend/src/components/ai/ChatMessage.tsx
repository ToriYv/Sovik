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

// src/components/ai/ChatMessage.tsx
"use client";

import React from "react";
import { Badge } from "../ui/Badge";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  stage?: string;
  data?: any; // ✅ Добавлен пропс data
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  stage,
  data,
}) => {
  const isUser = role === "user";

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
          <span className="text-primary-600 font-bold">AI</span>
        </div>
      )}
      <div className={`max-w-[80%] ${isUser ? "order-first" : ""}`}>
        {stage && !isUser && (
          <Badge variant="info" className="mb-2">
            {stage}
          </Badge>
        )}
        <div
          className={`p-4 rounded-xl ${
            isUser
              ? "bg-primary-600 text-white"
              : "bg-neutral-100 text-neutral-900"
          }`}
        >
          {content}

          {/* Отображение сгенерированного кода */}
          {data?.content && (
            <pre className="bg-neutral-800 text-white p-3 rounded mt-3 overflow-x-auto text-sm">
              <code>{data.content}</code>
            </pre>
          )}

          {/* Отображение анализа требований */}
          {data?.analysis && (
            <div className="mt-3 p-3 bg-neutral-200 rounded text-sm">
              <strong>Анализ требований:</strong>
              <ul className="list-disc list-inside mt-1">
                {Array.isArray(data.analysis.key_features) ? (
                  data.analysis.key_features.map((feature: any, index: number) => (
                    <li key={index}>
                      {Object.entries(feature).map(([key, value]) => (
                        <div key={key}>
                          <strong>{key}:</strong> {String(value)}
                        </div>
                      ))}
                    </li>
                  ))
                ) : (
                  <li>{JSON.stringify(data.analysis)}</li>
                )}
              </ul>
            </div>
          )}

          {/* Отображение спецификации дизайна */}
          {data?.props && (
            <div className="mt-3 p-3 bg-neutral-200 rounded text-sm">
              <strong>Спецификация компонента:</strong>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                {Object.entries(data.props).map(([propName, propSpec]: [string, any]) => (
                  <div key={propName} className="border-b pb-1">
                    <div><strong>{propName}</strong></div>
                    <div className="text-xs text-neutral-600">
                      {propSpec.type} - {propSpec.description}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
      {isUser && (
        <div className="w-8 h-8 rounded-full bg-neutral-800 flex items-center justify-center">
          <span className="text-white font-bold">Вы</span>
        </div>
      )}
    </div>
  );
};