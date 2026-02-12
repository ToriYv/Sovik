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

// apps/frontend/src/app/api/chat/route.ts
import { NextRequest } from "next/server";
import { generateComponent } from "@/lib/api";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { prompt, stream = false } = body;

    if (!prompt) {
      return Response.json({ error: "Prompt is required" }, { status: 400 });
    }

    // Вызываем FastAPI бэкенд напрямую
    const result = await generateComponent({ prompt, stream });

    return Response.json(result);
  } catch (error: any) {
    console.error("Chat API error:", error);
    return Response.json(
      { error: error.message || "Internal server error" },
      { status: 500 }
    );
  }
}