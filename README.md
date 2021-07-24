# Allan-yfinance-stock-chatbot
This is a simple RASA-NLU based financial stock chatbot. It can finish simple intent recognition, entity recognition and extraction, and slot filling tasks. Users can have small talk and multiple dialogues based on context with the chatbot.

## **Demo-video**
https://user-images.githubusercontent.com/31875506/126862796-860b718f-a4fe-4122-9533-e76bc2fbf58c.mp4

## Virtual environment

1. python==3.6.12 | rasa==0.15.1 | spacy==2.3.2 | tensorflow==2.1.1

2. Install the Anaconda and create the virtual environment.

3. Activate your virtual environment from Anaconda prompt.

4. Input the following command：

   ```python
   pip install -r requirements.txt

## If you just want to run my bot in your machines, here are suggestions:

1. For people in some regions, a fast VPN with American servers is recommended.

2. The chatbot uses the Telegram as its interface,yu need to create a bot of your own through [BotFather](https://telegram.me/botfather) and get api token. Then you should replace my token in the py file with the unique API token you applied for and change the chat id. Note that chat id and API token are two different things, check [Telegram APIs](https://core.telegram.org/api) or [stack overflow](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id) for more details.

3. Here is the configuration of RASA Pipeline, you can change it based on your need. [Check here and learn more about Pipeline](https://legacy-docs-v1.rasa.com/nlu/choosing-a-pipeline/)
  ```python
  language: "en"
  
  pipeline: "spacy_sklearn"
  ```
Keeping in mind that you should install the English spacy model after finishing the spacy installation. Using the following commands:
  ```python
  pip install -U spacy
  python -m spacy.en.download
  python -m spacy download en_core_web_sm
  ```

## Reference materials

[python-telegram-bot document](https://pypi.org/project/python-telegram-bot/3.4/)

[Rasa version 1.x document](https://legacy-docs-v1.rasa.com/)

[How to choose a pipelinne](https://legacy-docs-v1.rasa.com/nlu/choosing-a-pipeline/)

[spacy official website](https://spacy.io/)

[yfinance document](https://pypi.org/project/yfinance/)

[Yahoo Finance API](https://aroussi.com/post/python-yahoo-finance)
