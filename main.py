from openai import OpenAI

from config import settings


def main() -> None:
    client = OpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
    )

    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {
                "role": "system",
                "content": "你是一个简洁、可靠的AI助手。",
            },
            {
                "role": "user",
                "content": "请用一句话解释什么是AI Agent。",
            },
        ],
        temperature=0.6,
    )

    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
