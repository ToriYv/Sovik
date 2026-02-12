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

// src/app/page.tsx
import { ChatInterface } from "@/components/ai/ChatInterface"; // ← Правильный путь

export default function HomePage() {
  return (
    <div className="min-h-screen bg-neutral-50">
      <main className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-neutral-900 mb-6">
          Local AI Studio
        </h1>
        <div className="bg-white rounded-xl shadow-sm border border-neutral-200 overflow-hidden">
          <ChatInterface />
        </div>
      </main>
    </div>
  );
}