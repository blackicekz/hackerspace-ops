import unittest

from src.adapters.telegram_bootstrap import BootstrapCommand, reply_for
from src.infrastructure.config import ConfigurationError, load_bot_config

TEST_CHAT_ID = -100123456


class BootstrapReplyAcceptanceTest(unittest.TestCase):
    def test_start_in_test_group_replies_with_identification(self) -> None:
        reply = reply_for(BootstrapCommand(TEST_CHAT_ID, "/start", False), TEST_CHAT_ID)

        self.assertIsNotNone(reply)

    def test_help_in_test_group_replies_naming_supported_commands(self) -> None:
        reply = reply_for(BootstrapCommand(TEST_CHAT_ID, "/help", False), TEST_CHAT_ID)

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertIn("/start", reply)
        self.assertIn("/help", reply)

    def test_start_addressed_to_bot_username_is_recognized(self) -> None:
        reply = reply_for(
            BootstrapCommand(TEST_CHAT_ID, "/start@hackerspace_ops_bot", False), TEST_CHAT_ID
        )

        self.assertIsNotNone(reply)

    def test_command_outside_test_group_is_ignored(self) -> None:
        reply = reply_for(BootstrapCommand(TEST_CHAT_ID + 1, "/start", False), TEST_CHAT_ID)

        self.assertIsNone(reply)

    def test_unrecognized_text_in_test_group_is_ignored(self) -> None:
        reply = reply_for(BootstrapCommand(TEST_CHAT_ID, "hello there", False), TEST_CHAT_ID)

        self.assertIsNone(reply)

    def test_bot_authored_message_is_ignored_even_in_test_group(self) -> None:
        reply = reply_for(BootstrapCommand(TEST_CHAT_ID, "/start", True), TEST_CHAT_ID)

        self.assertIsNone(reply)


class BotConfigAcceptanceTest(unittest.TestCase):
    def test_valid_environment_loads_configuration(self) -> None:
        config = load_bot_config(
            {"TELEGRAM_BOT_TOKEN": "secret-token", "HACKERSPACE_TEST_CHAT_ID": "-100123"}
        )

        self.assertEqual("secret-token", config.telegram_bot_token)
        self.assertEqual(-100123, config.test_chat_id)
        self.assertEqual("INFO", config.log_level)

    def test_missing_token_fails_before_polling(self) -> None:
        with self.assertRaises(ConfigurationError):
            load_bot_config({"HACKERSPACE_TEST_CHAT_ID": "-100123"})

    def test_missing_chat_id_fails_before_polling(self) -> None:
        with self.assertRaises(ConfigurationError):
            load_bot_config({"TELEGRAM_BOT_TOKEN": "secret-token"})

    def test_non_integer_chat_id_fails_before_polling(self) -> None:
        with self.assertRaises(ConfigurationError):
            load_bot_config(
                {"TELEGRAM_BOT_TOKEN": "secret-token", "HACKERSPACE_TEST_CHAT_ID": "not-a-number"}
            )

    def test_error_message_names_variable_without_value(self) -> None:
        try:
            load_bot_config({"HACKERSPACE_TEST_CHAT_ID": "-100123"})
        except ConfigurationError as exc:
            self.assertIn("TELEGRAM_BOT_TOKEN", str(exc))
        else:
            self.fail("expected ConfigurationError")

    def test_custom_log_level_is_honored(self) -> None:
        config = load_bot_config(
            {
                "TELEGRAM_BOT_TOKEN": "secret-token",
                "HACKERSPACE_TEST_CHAT_ID": "-100123",
                "HACKERSPACE_LOG_LEVEL": "DEBUG",
            }
        )

        self.assertEqual("DEBUG", config.log_level)


if __name__ == "__main__":
    unittest.main()
