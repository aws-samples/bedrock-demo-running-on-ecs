########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

import boto3

from typing import Union
from fastapi import APIRouter
from pydantic import BaseModel

import os

# os.environ["AWS_REGION"] = "eu-central-1"

from .baml_client import b

dialog_router = APIRouter()


bedrock_runtime = boto3.client(
    service_name="bedrock-runtime", region_name="eu-central-1"
)

MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"


class UserPrompt(BaseModel):
    instruction: str


class Answer(BaseModel):
    text: str


@dialog_router.post("/prompt", response_model=Answer)
def create_answer(prompt: UserPrompt) -> Answer:
    input_text = prompt.instruction
    messages = [{"role": "user", "content": [{"text": input_text}]}]

    system = [{"text": "Respond only in Korean"}]

    # response = bedrock_runtime.converse(
    #     modelId=MODEL_ID, messages=messages, system=system
    # )
    print("input_text", input_text)
    response = b.ExtractResume(input_text)
    print("responseee", response)

    # output_message = response["output"]["message"]

    # output = "\n".join([content["text"] for content in output_message["content"]])
    # print(output)

    return Answer(text=response)
