"""
Prompt Engineering & LLM Integration Layer.

Responsible for generating deterministic, grounded prompts and
integrating with configurable LLM providers.

RESPONSIBILITIES:
- Build system, routing, recommendation, comparison, clarification, refusal, fallback prompts
- Render templates with structured context
- Estimate and optimize token usage
- Support multiple LLM providers (OpenAI, Groq, Gemini, Anthropic, etc.)
- Invoke LLM providers with retry and fallback
- Parse and validate structured outputs

DOES NOT:
- Perform business logic
- Make recommendations
- Perform comparisons
- Detect intents
- Run guardrails
- Retrieve documents

The LLM is responsible ONLY for natural language generation.
All reasoning has been completed by existing engines.
"""
