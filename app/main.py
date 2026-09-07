import argparse
import os
import sys
import json
import subprocess

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


"""
  what write actually does, 
  it going to extract the content of file and then going to write them into the another file 
"""


def executingWriteToolCall(arguments: dict):
    print("Writing tool is working ")
    file_path = arguments["file_path"]
    contentInFile = arguments["content"]

    # Creates the file if it doesn't exist.
    # If it already exists, overwrites it.
    with open(file_path, "w") as file:
        file.write(contentInFile)
    return "file content succesfully written"


"""
  what Bash actually does, 
  it going to complete the 
"""


def executingBashToolCall(arguments: dict):
    command = arguments["command"]

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    return output


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
        },
        {
            "type": "function",
            "function": {
                "name": "Write",
                "description": "Write content to a file",
                "parameters": {
                    "type": "object",
                    "required": ["file_path", "content"],
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path of the file to write to",
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "Bash",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "required": ["command"],
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The command to execute",
                        }
                    },
                },
            },
        },
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

        # if there is any toolCall;
        for tool_Call in message.tool_calls:
            # getting functionCall Name = Read, write, bash
            toolCallFunctionName = tool_Call.function.name
            jsonArguments = parseToJson(tool_Call.function.arguments)

            if toolCallFunctionName == "Read":
                # parsing the arguments as Json String

                toolCallResult = executingReadToolCall(jsonArguments)
                toolCallId = tool_Call.id

                userMessage.append(
                    {
                        "role": "tool",
                        "tool_call_id": toolCallId,
                        "content": toolCallResult,
                    }
                )
            if toolCallFunctionName == "Write":
                # parses the arguments and file_Path and content;
                toolCallFunctionName = tool_Call.function.name
                writeToolCallResult = executingWriteToolCall(jsonArguments)
                toolCallId = tool_Call.id
                userMessage.append(
                    {
                        "role": "tool",
                        "tool_call_id": toolCallId,
                        "content": writeToolCallResult,
                    }
                )
                print(writeToolCallResult)

            if toolCallFunctionName == "Bash":
                # Parse the arguments to extract the command
                bashToolCallResult = executingBashToolCall(jsonArguments)
                print(bashToolCallResult)
                toolCallId = tool_Call.id
                userMessage.append(
                    {
                        "role": "tool",
                        "tool_call_id": toolCallId,
                        "content": bashToolCallResult,
                    }
                )

    # You can use print statements as follows for debugging, they'll be visible when running tests.

    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
