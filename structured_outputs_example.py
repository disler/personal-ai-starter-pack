# https://openai.com/index/introducing-structured-outputs-in-the-api/

from enum import Enum
from typing import Union

from pydantic import BaseModel

import openai
from openai import OpenAI

NEW_GPT_4o_AUG = "gpt-4o-2024-08-06"


def structured_output_tool_call():

    class Table(str, Enum):
        orders = "orders"
        customers = "customers"
        products = "products"

    class Column(str, Enum):
        id = "id"
        status = "status"
        expected_delivery_date = "expected_delivery_date"
        delivered_at = "delivered_at"
        shipped_at = "shipped_at"
        ordered_at = "ordered_at"
        canceled_at = "canceled_at"

    class Operator(str, Enum):
        eq = "="
        gt = ">"
        lt = "<"
        le = "<="
        ge = ">="
        ne = "!="

    class OrderBy(str, Enum):
        asc = "asc"
        desc = "desc"

    class DynamicValue(BaseModel):
        column_name: str

    class Condition(BaseModel):
        column: str
        operator: Operator
        value: Union[str, int, DynamicValue]

    class Query(BaseModel):
        table_name: Table
        columns: list[Column]
        conditions: list[Condition]
        order_by: OrderBy

    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model=NEW_GPT_4o_AUG,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. The current date is August 6, 2024. You help users query for the data they are looking for by calling the query function.",
            },
            {
                "role": "user",
                "content": "Find all the orders that were cancelled in the first quarter of 2022",
            },
        ],
        tools=[
            openai.pydantic_function_tool(Query),
        ],
    )

    def mock_query_function(query: Query):
        print(f"Table Name: {query.table_name}")
        print("Columns:")
        for column in query.columns:
            print(f"  - {column}")
        print("Conditions:")
        for condition in query.conditions:
            print(
                f"  - Column: {condition.column}, Operator: {condition.operator}, Value: {condition.value}"
            )
        print(f"Order By: {query.order_by}")

    print(
        "completion.choices and completion.choices[0].message",
        completion.choices and completion.choices[0].message,
    )

    # Parse the completion result and pass it to the mock function if available
    if completion.choices and completion.choices[0].message.tool_calls:
        if completion.choices[0].message.tool_calls[0].function.name == "Query  ":
            query_result = (
                completion.choices[0].message.tool_calls[0].function.parsed_arguments
            )
            mock_query_function(query_result)
        else:
            print(f"{completion.choices and completion.choices[0].message.content}")
    else:
        print(f"{completion.choices and completion.choices[0].message.content}")


def structured_output_minimal():

    class Step(BaseModel):
        explanation: str
        output: str

    class MathResponse(BaseModel):
        steps: list[Step]
        final_answer: str

    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model=NEW_GPT_4o_AUG,
        messages=[
            {"role": "system", "content": "You are a helpful math tutor."},
            {"role": "user", "content": "solve 8x + 31 = 2"},
        ],
        response_format=MathResponse,
    )

    message = completion.choices[0].message
    if message.parsed:
        print(message.parsed.steps)
        print(message.parsed.final_answer)
    else:
        print(message.refusal)


structured_output_minimal()
structured_output_tool_call()
