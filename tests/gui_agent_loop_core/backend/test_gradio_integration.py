import os
import tempfile
import time
import unittest
from unittest.mock import patch

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from gui_agent_loop_core.backend.sandbox.sandbox_server_impl_gradio import DummyGuiAgentInterpreter, sandbox_server
from gui_agent_loop_core.core.interpreter_manager import InterpreterManager


class TestGradioIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 一意の `user-data-dir` を作成（競合防止）
        user_data_dir = tempfile.mkdtemp()

        # Chrome オプションを設定
        options = Options()
        options.add_argument("--headless")  # UIなしで動作（CI環境向け）
        options.add_argument("--no-sandbox")  # サンドボックスを無効化（権限問題回避）
        options.add_argument("--disable-dev-shm-usage")  # 共有メモリ問題を回避
        options.add_argument(f"--user-data-dir={user_data_dir}")  # 競合しないプロファイルを使用

        try:
            # `webdriver_manager` を使用して `chromedriver` を取得
            service = Service(ChromeDriverManager().install())
            cls.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"WebDriver の起動に失敗しました: {e}")
            raise  # エラーを発生させてテストを中断

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "driver"):
            cls.driver.quit()  # Chrome を適切に終了

    def setUp(self):
        interpreter = DummyGuiAgentInterpreter()
        interpreter_manager = InterpreterManager(interpreter)
        self.app = sandbox_server(interpreter_manager, test_mode=True)
        self.app.launch(share=True)

    def tearDown(self):
        self.app.close()

    def test_gradio_ui_interactions(self):
        input_box = self.driver.find_element(By.TAG_NAME, "input")
        input_box.send_keys("Hello, how are you?")
        input_box.send_keys(Keys.RETURN)

        wait = WebDriverWait(self.driver, 10)
        response = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "output")))

        self.assertIn("chat_core response", response.text)

    def test_streaming_response_from_llm(self):
        input_box = self.driver.find_element(By.TAG_NAME, "input")
        input_box.send_keys("Stream this response")
        input_box.send_keys(Keys.RETURN)

        wait = WebDriverWait(self.driver, 10)
        response = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "output")))

        self.assertIn("chat_core response", response.text)

    def test_synchronous_response_from_llm(self):
        input_box = self.driver.find_element(By.TAG_NAME, "input")
        input_box.send_keys("Give me a synchronous response")
        input_box.send_keys(Keys.RETURN)

        wait = WebDriverWait(self.driver, 10)
        response = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "output")))

        self.assertIn("chat_core response", response.text)


if __name__ == "__main__":
    unittest.main()
