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

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  stage?: string;
  data?: any; //
}

export interface GenerateRequest {
  prompt: string;
  stream?: boolean;
}

export interface GenerateResponse {
  success: boolean;
  data: any;
  error?: string;
}

export interface ComponentSpec {
  name: string;
  props: Record<string, any>;
  variants: Record<string, string[]>;
  slots: string[];
  tailwind_classes: any;
  example_usage: string;
}

