import argparse
import os
import sys
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


# if os.path.exists(filePath):
#         if os.path.isdir(filePath):
#             print("\n".join(os.listdir(filePath)))
#         else:
#             with open(filePath, "r") as f:
#                 print(f.read(), end="")
#     else:
#         pass


def parseToJson(objectValue: str):
    jsonValue = json.loads(objectValue)
    return jsonValue


"""
    what actually read tool does
       1. its open the file if its exits
       2.read the contents of it simple and print its
"""


def executingReadToolCall(argument: dict):
    # getting fileName
    filePath = argument["file_path"]

    # see if its exist
    if os.path.exists(filePath):
        if os.path.isdir(filePath):
            print("\n".join(os.listdir(filePath)))
        else:
            # open the file as in read mode
            with open(filePath, "r") as f:
                print(f.read(), end="")
    else:
        pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    # creating client for openai
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    userMessage = [{"role": "user", "content": args.p}]

    apiResponse = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=userMessage,
        max_tokens=1000,
        tools=[
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
        ],
    )

    # checking whether llm is responding or not;
    if not apiResponse or len(apiResponse.choices) == 0:
        raise RuntimeError("no choices in response")

    # llm responsed with stuff
    # print(apiResponse.choices[0].message.content)

    # increasing the context of my llm with newResponse;
    userMessage.append(apiResponse.choices[0].message.content)

    # if there is any tool cool;
    if apiResponse.choices[0].message.tool_calls:
        # getting functionCall Name = Read, write, bash
        toolCallFunctionName = (
            apiResponse.choices[0].message.tool_calls[0].function.name
        )

        # parsing the arguments as Json String
        jsonArguments = parseToJson(
            apiResponse.choices[0].message.tool_calls[0].function.arguments
        )

        if toolCallFunctionName == "Read":
            executingReadToolCall(jsonArguments)

        # print("function call name ", toolCallFunctionName)
        # print("its json Arguments", jsonArguments)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()


# is llm using any tool calls;
# print()


# # persistant memeory
# memoryContext = []

# # calling the openAI api key;
# client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
# message = [{"role": "user", "content": args.p}]

# # api calling
# chat = client.chat.completions.create(
#     model="anthropic/claude-haiku-4.5",
#     messages=message,
#     max_tokens=1000,
#     tools=[
#         {
#             "type": "function",
#             "function": {
#                 "name": "Read",
#                 "description": "Read and return the contents of a file",
#
#             },
#         }
#     ],
# )

# #  chat is the response from my llm
# memoryContext.append(message)
# # memoryContext.append(message)

# choice = chat.choices[0]

# # Check if there's a tool call
# while choice.message.tool_calls:
#     # Extract the tool call
#     firstToolCall = choice.message.tool_calls[0]

#     # Parse the function name
#     tool_Name = firstToolCall.function.name
#     # Parse the arguments

#     tool_Args = parseToJson(firstToolCall.function.arguments)

#     # reading a file operation
#     filePath = tool_Args["file_path"]
#     if os.path.exists(filePath):
#         if os.path.isdir(filePath):
#             print("\n".join(os.listdir(filePath)))
#         else:
#             with open(filePath, "r") as f:
#                 print(f.read(), end="")
#     else:
#         pass

# else:
#     if choice.message.content:
#         print(choice.message.content)

# if not chat.choices or len(chat.choices) == 0:
#     raise RuntimeError("no choices in response")
