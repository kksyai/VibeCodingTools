import re
import copy
import math
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

    scores: dict[str, int] = {}
    for category, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        scores[category] = score

    best = max(scores, key=lambda key: scores[key])
    return best if scores[best] > 0 else "utils"


def build_new_tool(resource: dict) -> dict:
    return {
        "id": generate_resource_id(resource["name"]),
        "name": resource["name"],
        "url": resource["url"],
        "description": resource["description"],
        "icon": resource["icon"],
    }


def flatten_resources(data: dict) -> list[dict]:
    resources = []
    for category in data.get("categories", {}).values():
        category_name = category.get("name", "Без категории")
        for tool in category.get("tools", []):
            resources.append(
                {
                    "name": tool.get("name", "Без названия"),
                    "url": tool.get("url", ""),
                    "description": tool.get("description", ""),
                    "category_name": category_name,
                }
            )

    resources.sort(key=lambda item: (item["category_name"].lower(), item["name"].lower()))
    return resources


def build_list_page_text(resources: list[dict], page: int, page_size: int) -> tuple[str, int, int]:
    if page_size < 1:
        page_size = 10

    total = len(resources)
    total_pages = max(1, math.ceil(total / page_size))
    page = min(max(0, page), total_pages - 1)
    start = page * page_size
    end = start + page_size
    items = resources[start:end]

    lines = [f"Страница {page + 1}/{total_pages} · Всего: {total}", ""]

    if not items:
        lines.append("Список пока пуст")
        return "\n".join(lines), page, total_pages

    current_category = None
    for tool in items:
        category_name = tool["category_name"]
        if category_name != current_category:
            if current_category is not None:
                lines.append("")
            lines.append(category_name)
            current_category = category_name

        lines.append(f"- {tool['name']} - {tool['url']}")

    return "\n".join(lines), page, total_pages


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
