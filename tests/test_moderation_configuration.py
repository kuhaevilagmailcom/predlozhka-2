import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import main


class ModerationConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_no_legacy_moderation_group_fallback(self):
        with patch.object(main, "MODERATION_ENV", ""), patch.object(
            main, "resolved_moderation_chat_id", None
        ):
            self.assertIsNone(main.moderation_chat_value())

    async def test_positive_user_id_is_rejected_without_api_request(self):
        bot = SimpleNamespace(get_chat=AsyncMock())
        with patch.object(main, "MODERATION_ENV", "5374190089"), patch.object(
            main, "resolved_moderation_chat_id", None
        ):
            problem = await main.moderation_configuration_issue(bot)
        self.assertIn("положительный ID пользователя", problem)
        bot.get_chat.assert_not_awaited()

    async def test_actual_group_is_accepted(self):
        bot = SimpleNamespace(
            get_chat=AsyncMock(
                return_value=SimpleNamespace(id=-1001234567890, type="supergroup")
            )
        )
        with patch.object(main, "MODERATION_ENV", "-1001234567890"), patch.object(
            main, "resolved_moderation_chat_id", None
        ), patch.object(main, "resolved_destination_chat_id", -1009876543210):
            self.assertIsNone(await main.moderation_configuration_issue(bot))

    async def test_channel_cannot_be_moderation_group(self):
        bot = SimpleNamespace(
            get_chat=AsyncMock(
                return_value=SimpleNamespace(id=-1001234567890, type="channel")
            )
        )
        with patch.object(main, "MODERATION_ENV", "-1001234567890"), patch.object(
            main, "resolved_moderation_chat_id", None
        ), patch.object(main, "resolved_destination_chat_id", -1009876543210):
            problem = await main.moderation_configuration_issue(bot)
        self.assertIn("не на группу", problem)

    async def test_moderation_and_publication_must_be_separate(self):
        bot = SimpleNamespace(
            get_chat=AsyncMock(
                return_value=SimpleNamespace(id=-1001234567890, type="supergroup")
            )
        )
        with patch.object(main, "MODERATION_ENV", "-1001234567890"), patch.object(
            main, "resolved_moderation_chat_id", None
        ), patch.object(main, "resolved_destination_chat_id", -1001234567890):
            problem = await main.moderation_configuration_issue(bot)
        self.assertIn("одинаковый ID", problem)


if __name__ == "__main__":
    unittest.main()
