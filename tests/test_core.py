import unittest
from unittest.mock import AsyncMock

import httpx

from bot.core import (
    append_resource_with_retry,
    classify_resource,
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
