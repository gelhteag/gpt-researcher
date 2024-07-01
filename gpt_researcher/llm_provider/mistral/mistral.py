import os
import logging

from colorama import Fore, Style
from langchain_mistralai import ChatMistralAI


class MistralProvider:

    def __init__(
            self,
            model,
            temperature,
            max_tokens
    ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = self.get_api_key()
        self.llm = self.get_llm_model()
        

    def get_api_key(self):
        """
        Gets the Mistral API key
        Returns:

        """
        try:
            api_key = os.environ["MISTRAL_API_KEY"]
        except KeyError:
            raise Exception(
                "Mistral API key not found. Please set the MISTRAL_API_KEY environment variable.")
        return api_key

    def get_endpoint(self):
        """
        Gets the Mistral endpoint
        Returns:
            str: The endpoint URL
        """
        # Check if MISTRAL_ENDPOINT is set with a custom endpoint
        custom_endpoint = os.getenv("MISTRAL_ENDPOINT")
        if custom_endpoint:
            endpoint = custom_endpoint
        else:
            endpoint = "https://api.mistral.ai/v1"
            logging.warning("No custom endpoint provided. Using default endpoint: https://api.mistral.ai/v1. If you need to use another provider, please set the MISTRAL_ENDPOINT environment variable.")
        
        return endpoint

    def get_llm_model(self):
        # Initializing the chat model
        llm = ChatMistralAI(
            endpoint=self.get_endpoint(),
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key
        )

        return llm

    async def get_chat_response(self, messages, stream, websocket=None):
        if not stream:
            # Getting output from the model chain using ainvoke for asynchronous invoking
            output = await self.llm.ainvoke(messages)
            return output.content

        else:
            return await self.stream_response(messages, websocket)

    async def stream_response(self, messages, websocket=None):
        paragraph = ""
        response = ""

        # Streaming the response using the chain astream method from langchain
        async for chunk in self.llm.astream(messages):
            content = chunk.content
            if content is not None:
                response += content
                paragraph += content
                if "\n" in paragraph:
                    if websocket is not None:
                        await websocket.send_json({"type": "report", "output": paragraph})
                    else:
                        print(f"{Fore.GREEN}{paragraph}{Style.RESET_ALL}")
                    paragraph = ""

        return response
