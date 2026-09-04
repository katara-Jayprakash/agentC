import argparse
import os
import sys
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    chat = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=[{"role": "user", "content": args.p}],
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

    def parseToJson(objectValue):
        jsonValue = json.loads(objectValue)
        return jsonValue

    choice = chat.choices[0]
    # Check if there's a tool call
    if choice.message.tool_calls:
        # Extract the tool call
        firstToolCall = choice.message.tool_calls[0]

        # Parse the function name
        tool_Name = firstToolCall.function.name
        # Parse the arguments

        print("tool_Name", tool_Name)
        tool_Args = parseToJson(firstToolCall.function.arguments)
        print("argument value after parsing ", tool_Args)

        # reading a file operation
        filePath = tool_Args["file_path"]
        if os.path.exists(filePath):
            if os.path.isdir(filePath):
                print("\n".join(os.listdir(filePath)))
            else:
                with open(filePath, "r") as f:
                    print(f.read())
        else:
            pass
    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage
    print(chat.choices[0].message.content)


if __name__ == "__main__":
    main()
