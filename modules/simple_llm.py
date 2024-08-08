import llm
from dotenv import load_dotenv
import os

load_dotenv()


def prompt(model: llm.Model, prompt: str):
    res = model.prompt(prompt)
    return res.text()


def get_model_name(model: llm.Model):
    return model.model_id


def build_models():
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    sonnet_3_5_model: llm.Model = llm.get_model("claude-3.5-sonnet")
    sonnet_3_5_model.key = ANTHROPIC_API_KEY

    return sonnet_3_5_model


def build_big_3_models():
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    sonnet_3_5_model: llm.Model = llm.get_model("claude-3.5-sonnet")
    sonnet_3_5_model.key = ANTHROPIC_API_KEY

    gpt4_o_model: llm.Model = llm.get_model("4o")
    gpt4_o_model.key = OPENAI_API_KEY

    gemini_1_5_pro_model: llm.Model = llm.get_model("gemini-1.5-pro-latest")
    gemini_1_5_pro_model.key = GEMINI_API_KEY

    return sonnet_3_5_model, gpt4_o_model, gemini_1_5_pro_model


def build_big_3_plus_mini_models():

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    sonnet_3_5_model: llm.Model = llm.get_model("claude-3.5-sonnet")
    sonnet_3_5_model.key = ANTHROPIC_API_KEY

    gpt4_o_model: llm.Model = llm.get_model("4o")
    gpt4_o_model.key = OPENAI_API_KEY

    gemini_1_5_pro_model: llm.Model = llm.get_model("gemini-1.5-pro-latest")
    gemini_1_5_pro_model.key = GEMINI_API_KEY

    gpt4_o_mini_model: llm.Model = llm.get_model("gpt-4o-mini")
    gpt4_o_mini_model.key = OPENAI_API_KEY

    return sonnet_3_5_model, gpt4_o_model, gemini_1_5_pro_model, gpt4_o_mini_model


def build_mini_model():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    gpt4_o_mini_model: llm.Model = llm.get_model("gpt-4o-mini")
    gpt4_o_mini_model.key = OPENAI_API_KEY

    return gpt4_o_mini_model


def build_new_gpt4o():
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    gpt4_o_model: llm.Model = llm.get_model("gpt-4o-2024-08-06")
    gpt4_o_model.key = OPENAI_API_KEY

    return gpt4_o_model
