import re
import copy
from collections.abc import Mapping

import httpx


REQUIRED_ENV_VARS = ("TELEGRAM_BOT_TOKEN", "GITHUB_TOKEN")


keywords_map = {
    "ai-models": ["AI", "LLM", "API", "model", "OpenAI", "Claude", "Gemini", "GLM"],
    "ai-editors": ["editor", "IDE", "cursor", "coding", "agent", "bot", "assistant", "Monica", "Claude Code"],
    "skills-mcp": ["MCP", "skill", "Beads", "context", "agent"],
    "deploy": ["deploy", "hosting", "Vercel", "Railway", "Render", "Supabase", "serverless", "cloud"],
    "design": ["design", "UI", "Canva", "Dribbble", "Figma", "UI/UX", "interface", "style"],
    "docs": ["docs", "documentation", "React", "Tailwind", "framework", "guide", "reference", "Telegram"],
    "utils": ["tool", "utility", "productivity", "screenshot", "note", "capture", "record", "converter"],
}


def validate_required_env(env: Mapping[str, str]) -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not (env.get(name) or "").strip()]
    if missing:
        raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")


def generate_resource_id(name: str) -> str:
    cleaned = name.lower().replace(".", "")
    normalized = re.sub(r"[^a-z0-9]+", "-", cleaned).strip("-")
    return normalized or "resource"


def classify_resource(url: str, title: str = "", description: str = "") -> str:
    text = f"{url} {title} {description}".lower()

    scores = {}
    for category, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[category] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "utils"


def build_new_tool(resource: dict) -> dict:
    return {
        "id": generate_resource_id(resource["name"]),
        "name": resource["name"],
        "url": resource["url"],
        "description": resource["description"],
        "icon": resource["icon"],
    }


async def append_resource_with_retry(resource: dict, read_fn, write_fn, max_retries: int = 1) -> str:
    category = resource["category"]

    for attempt in range(max_retries + 1):
        data, sha = await read_fn()

        if category not in data["categories"]:
            raise ValueError(f"Категория '{category}' не найдена")

        new_tool = build_new_tool(resource)
        existing_ids = {tool["id"] for tool in data["categories"][category]["tools"]}
        if new_tool["id"] in existing_ids:
            return "exists"

        updated_data = copy.deepcopy(data)
        updated_data["categories"][category]["tools"].append(new_tool)

        try:
            await write_fn(
                updated_data,
                sha,
                f"add: {resource['name']} to {data['categories'][category]['name']}",
            )
            return "added"
        except httpx.HTTPStatusError as exc:
            if exc.response is not None and exc.response.status_code == 409 and attempt < max_retries:
                continue
            raise

    return "error"
