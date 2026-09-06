import argparse
import os
import sys
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def parseToJson(objectValue: str):
    jsonValue = json.loads(objectValue)
    return jsonValue


"""
    what actually read tool does
       1. its open the file if its exits
       2.read the contents of it simple and print its
"""


def executingReadToolCall(argument: dict):
    # getting the file name
    filePath = argument["file_path"]

    # see if the file exits
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            return "\n".join(os.listdir(filePath))
        else:
            with open(filePath, "r") as f:
                return f.read()
    else:
        return f"File not found: {filePath}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    # creating client for openai
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    userMessage = [{"role": "user", "content": args.p}]

    supportedTools = [
        {
            "type": "function",
            "function": {
                "name": "Read",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        }
    ]

    while True:
        # api calling;
        apiResponse = client.chat.completions.create(
            model="anthropic/claude-haiku-4.5",
            messages=userMessage,
            max_tokens=1000,
            tools=supportedTools,
        )

        # checking whether llm is responding or not;
        if not apiResponse or len(apiResponse.choices) == 0:
            raise RuntimeError("no choices in response")

        message = apiResponse.choices[0].message

        #  record this iteration's assistant message
        userMessage.append(message)

        # if there is no toolCall just break the loop
        if not message.tool_calls:
            print(message.content)
            break

        # if there is any tool cool;
        for tool_Call in message.tool_calls:
            # getting functionCall Name = Read, write, bash
            toolCallFunctionName = tool_Call.function.name

            # parsing the arguments as Json String
            jsonArguments = parseToJson(tool_Call.function.arguments)

            if toolCallFunctionName == "Read":
                toolCallResult = executingReadToolCall(jsonArguments)
                toolCallId = tool_Call.id

                userMessage.append(
                    {
                        "role": "tool",
                        "tool_call_id": toolCallId,
                        "content": toolCallResult,
                    }
                )

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
