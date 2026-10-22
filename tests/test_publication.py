"""Publication should never append automatically generated text to accepted posts."""
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import main


class PublicationTests(unittest.IsolatedAsyncioTestCase):
    async def test_single_message_only_copied_without_disclaimer(self):
        bot = SimpleNamespace(
            copy_message=AsyncMock(return_value=SimpleNamespace(message_id=55)),
            send_message=AsyncMock(),
            edit_message_text=AsyncMock(),
            edit_message_caption=AsyncMock(),
        )
        submission = {"user_id": 4321}
        items = [{"message_id": 12}]
        with patch.object(main.db, "get", return_value=submission), patch.object(
            main.db, "items_for_submission", return_value=items
        ):
            ids, control_id = await main.copy_submission(
                bot, -1001234567890, 88, moderation_controls=False
            )
        self.assertEqual((ids, control_id), ([55], None))
        bot.copy_message.assert_awaited_once_with(
            chat_id=-1001234567890, from_chat_id=4321, message_id=12
        )
        bot.send_message.assert_not_awaited()
        bot.edit_message_text.assert_not_awaited()
        bot.edit_message_caption.assert_not_awaited()

    async def test_album_copied_without_extra_messages(self):
        bot = SimpleNamespace(
            copy_messages=AsyncMock(
                return_value=[
                    SimpleNamespace(message_id=55),
                    SimpleNamespace(message_id=56),
                ]
            ),
            send_message=AsyncMock(),
            edit_message_caption=AsyncMock(),
        )
        submission = {"user_id": 4321}
        items = [{"message_id": 12}, {"message_id": 13}]
        with patch.object(main.db, "get", return_value=submission), patch.object(
            main.db, "items_for_submission", return_value=items
        ):
            ids, control_id = await main.copy_submission(
                bot, -1001234567890, 88, moderation_controls=False
            )
        self.assertEqual((ids, control_id), ([55, 56], None))
        bot.copy_messages.assert_awaited_once_with(
            chat_id=-1001234567890, from_chat_id=4321, message_ids=[12, 13]
        )
        bot.send_message.assert_not_awaited()
        bot.edit_message_caption.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
