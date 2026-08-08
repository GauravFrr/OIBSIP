import unittest
from unittest.mock import patch, MagicMock
from voice_assistant import get_time, get_date, handle_command, get_weather, search_wikipedia, open_website

class TestVoiceAssistant(unittest.TestCase):

    def test_get_time(self):
        # Verify get_time returns a non-empty string in AM/PM format
        time_str = get_time()
        self.assertIsInstance(time_str, str)
        self.assertTrue(time_str.endswith("AM") or time_str.endswith("PM"))

    def test_get_date(self):
        # Verify get_date returns a non-empty string
        date_str = get_date()
        self.assertIsInstance(date_str, str)
        self.assertGreater(len(date_str), 0)

    def test_handle_command_chat(self):
        # Test basic greetings and conversations
        self.assertEqual(handle_command("hello"), "Hello! How can I help you today?")
        self.assertEqual(handle_command("how are you"), "I'm doing great, thank you for asking! How are you?")
        self.assertEqual(handle_command("what's your name"), "I am your Python Voice Assistant. You can call me helper.")
        self.assertEqual(handle_command("thank you"), "You're very welcome!")
        self.assertEqual(handle_command("bye"), "Goodbye! Have a nice day!")

    def test_handle_command_time_date(self):
        # Test time and date command routing
        self.assertIn("The current time is", handle_command("what is the time"))
        self.assertIn("Today's date is", handle_command("what is today's date"))

    def test_handle_command_weather_routing(self):
        # Test routing when city is not specified
        self.assertEqual(
            handle_command("check weather"),
            "Which city would you like to check the weather for? E.g. say 'weather in Paris'."
        )

    def test_handle_command_open_website_routing(self):
        # Test routing when website is not specified
        self.assertEqual(
            handle_command("open"),
            "Which site would you like me to open? E.g. 'open google'."
        )

    def test_handle_command_fallback(self):
        # Test unrecognized command fallback response
        self.assertEqual(
            handle_command("random unrecognized query"),
            "I didn't quite catch that. Can you try again or ask something else?"
        )

    @patch("webbrowser.open")
    def test_open_website(self, mock_browser):
        # Test opening mapped sites
        response = open_website("youtube")
        self.assertEqual(response, "Opening youtube.")
        mock_browser.assert_called_once_with("https://www.youtube.com")

    @patch("webbrowser.open")
    def test_open_website_fallback(self, mock_browser):
        # Test opening unmapped sites searches google
        response = open_website("python.org")
        self.assertIn("Searching Google for", response)
        mock_browser.assert_called_once_with("https://www.google.com/search?q=python.org")

    @patch("wikipedia.summary")
    def test_search_wikipedia(self, mock_summary):
        # Test successful wikipedia query
        mock_summary.return_value = "Python is a programming language. It is widely used."
        response = search_wikipedia("python programming")
        self.assertEqual(response, "Python is a programming language. It is widely used.")
        mock_summary.assert_called_once_with("python programming", sentences=2)

    @patch("requests.get")
    def test_get_weather_no_key(self, mock_get):
        # Test weather behavior when API key is unconfigured (temporarily override config value)
        with patch("voice_assistant.WEATHER_API_KEY", ""):
            response = get_weather("London")
            self.assertIn("API key is not configured", response)

    @patch("wikipedia.summary")
    def test_handle_command_wikipedia_routing(self, mock_summary):
        mock_summary.return_value = "Python is a programming language."
        self.assertEqual(
            handle_command("search programming language"),
            "Python is a programming language."
        )
        self.assertEqual(
            handle_command("look up programming language"),
            "Python is a programming language."
        )

if __name__ == "__main__":
    unittest.main()
