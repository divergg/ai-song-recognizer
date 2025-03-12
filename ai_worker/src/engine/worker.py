import copy
import json

import httpx
from httpx_socks import AsyncProxyTransport, SyncProxyTransport
from src.configs import settings
from autogen import UserProxyAgent, AssistantAgent

from src.engine.enums import QueryStatus
from src.engine.functions import get_lyrics

from src.engine.prompts import LYRICS_ANALYSIS_PROMPT, COUNTRY_CALCULATION_PROMPT

from common_utils.log_util import setup_file_logger


logger = setup_file_logger(
    name="ai_logger", log_file="ai_logger.log")

class MyHttpClient(httpx.Client):
    def __deepcopy__(self, memo):
        return self

class Engine:

    def __init__(
        self
    ) -> None:
        self.http_client = None
        if settings.ai.proxy_url:
            transport = SyncProxyTransport.from_url(settings.ai.proxy_url)
            self.http_client = MyHttpClient(transport=transport)

        self.llm_config = {"config_list": [{"model": settings.ai.model, "api_key": settings.ai.token, "http_client": self.http_client}], "temperature": 0.0}

    async def query(
        self, artist: str, title: str
    ) -> dict:
        """Make GPT queries"""

        default_response = "Could not retrieve track lyrics. Try again later"

        lyrics = await get_lyrics(artist=artist, title=title)
        logger.info(f'PROVIDED LYRICS - {lyrics}')
        if not lyrics:
            return {"response": default_response, "countries": []}

        user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            llm_config=copy.deepcopy(self.llm_config)
        )

        lyrics_analysis_agent = AssistantAgent(
            name="func_execution_agent",
            llm_config=copy.deepcopy(self.llm_config),
            system_message=LYRICS_ANALYSIS_PROMPT,
        )

        country_calculation_agent = AssistantAgent(
            name="func_execution_agent",
            llm_config=copy.deepcopy(self.llm_config),
            system_message=COUNTRY_CALCULATION_PROMPT,
        )


        lyrics_analysis = await user_proxy.a_initiate_chat(
            lyrics_analysis_agent, message=lyrics, max_turns=1, summary_method="last_msg"
        )

        country_list = await user_proxy.a_initiate_chat(
            country_calculation_agent, message=lyrics, max_turns=1, summary_method="last_msg"
        )

        logger.info(f'LYRICS ANALYSIS - {lyrics_analysis.summary}.\n COUNTRY LIST - {country_list.summary}')

        country_list = json.loads(country_list.summary)


        return {
            "response": lyrics_analysis.summary, "countries": country_list
        }





