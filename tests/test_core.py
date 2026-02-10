import unittest
from unittest.mock import AsyncMock

import httpx

from bot.core import (
    append_resource_with_retry,
    build_list_page_text,
    classify_resource,
    flatten_resources,
    generate_resource_id,
    validate_required_env,
)


class CoreTests(unittest.IsolatedAsyncioTestCase):
    def test_validate_required_env_reports_missing(self):
        with self.assertRaises(RuntimeError) as err:
            validate_required_env({"TELEGRAM_BOT_TOKEN": "ok", "GITHUB_TOKEN": ""})
        self.assertIn("GITHUB_TOKEN", str(err.exception))

    def test_generate_resource_id_normalizes_name(self):
        resource_id = generate_resource_id("My Tool.io / v2")
        self.assertEqual(resource_id, "my-toolio-v2")

    def test_classify_resource_defaults_to_utils_without_keyword_hits(self):
        category = classify_resource("https://example.com", "Unknown", "No keyword")
        self.assertEqual(category, "utils")

    def test_flatten_resources_sorts_by_category_then_name(self):
        data = {
            "categories": {
                "utils": {
                    "name": "Утилиты",
                    "tools": [
                        {"name": "Zeta", "url": "https://z.example"},
                        {"name": "Alpha", "url": "https://a.example"},
                    ],
                },
                "ai-models": {
                    "name": "AI-модели",
                    "tools": [
                        {"name": "Beta", "url": "https://b.example"},
                    ],
                },
            }
        }

        resources = flatten_resources(data)

        self.assertEqual(resources[0]["category_name"], "AI-модели")
        self.assertEqual(resources[0]["name"], "Beta")
        self.assertEqual(resources[1]["name"], "Alpha")
        self.assertEqual(resources[2]["name"], "Zeta")

    def test_build_list_page_text_returns_page_and_total_pages(self):
        resources = [
            {"name": "Tool 1", "url": "https://1.example", "category_name": "Cat"},
            {"name": "Tool 2", "url": "https://2.example", "category_name": "Cat"},
            {"name": "Tool 3", "url": "https://3.example", "category_name": "Cat"},
        ]

        text, page, total_pages = build_list_page_text(resources, page=1, page_size=2)

        self.assertIn("Страница 2/2", text)
        self.assertIn("Tool 3", text)
        self.assertEqual(page, 1)
        self.assertEqual(total_pages, 2)

    def test_build_list_page_text_handles_empty_list(self):
        text, page, total_pages = build_list_page_text([], page=0, page_size=5)

        self.assertIn("Всего: 0", text)
        self.assertIn("Список пока пуст", text)
        self.assertEqual(page, 0)
        self.assertEqual(total_pages, 1)

    async def test_append_resource_with_retry_retries_on_conflict(self):
        data = {
            "categories": {
                "utils": {
                    "name": "Utils",
                    "tools": [],
                }
            }
        }

        read_fn = AsyncMock(side_effect=[(data, "sha-old"), (data, "sha-new")])
        request = httpx.Request("PUT", "https://api.github.com/repos/x/y/contents/data/resources.json")
        response = httpx.Response(409, request=request)
        conflict = httpx.HTTPStatusError("conflict", request=request, response=response)
        write_fn = AsyncMock(side_effect=[conflict, None])

        status = await append_resource_with_retry(
            {
                "name": "Retry Tool",
                "url": "https://retry.example",
                "description": "desc",
                "icon": "https://example/icon.png",
                "category": "utils",
            },
            read_fn=read_fn,
            write_fn=write_fn,
            max_retries=1,
        )

        self.assertEqual(status, "added")
        self.assertEqual(read_fn.await_count, 2)
        self.assertEqual(write_fn.await_count, 2)

    async def test_append_resource_with_retry_skips_duplicate_id(self):
        data = {
            "categories": {
                "utils": {
                    "name": "Utils",
                    "tools": [
                        {
                            "id": "retry-tool",
                            "name": "Retry Tool",
                            "url": "https://retry.example",
                            "description": "desc",
                            "icon": "https://example/icon.png",
                        }
                    ],
                }
            }
        }

        read_fn = AsyncMock(return_value=(data, "sha"))
        write_fn = AsyncMock()

        status = await append_resource_with_retry(
            {
                "name": "Retry Tool",
                "url": "https://retry.example",
                "description": "desc",
                "icon": "https://example/icon.png",
                "category": "utils",
            },
            read_fn=read_fn,
            write_fn=write_fn,
            max_retries=1,
        )

        self.assertEqual(status, "exists")
        self.assertEqual(write_fn.await_count, 0)


if __name__ == "__main__":
    unittest.main()
