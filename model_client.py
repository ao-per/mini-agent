from typing import Any, Protocol

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from config import settings


class CompletionClient(Protocol):
    """Agent 所依赖的最小模型接口，便于在测试中注入假模型。"""

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> Any: ...


class ModelClientError(RuntimeError):
    def __init__(
        self,
        code: str,
        message: str,
        retryable: bool,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable


class ModelClient:
    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            timeout=settings.model_timeout_seconds,
            max_retries=settings.model_max_retries,
        )
        self._model = settings.model

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ):
        try:
            return self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )

        except AuthenticationError as exc:
            raise ModelClientError(
                code="AUTHENTICATION_ERROR",
                message="模型服务认证失败，请检查 API Key。",
                retryable=False,
            ) from exc

        except PermissionDeniedError as exc:
            raise ModelClientError(
                code="PERMISSION_DENIED",
                message=("当前 API Key 没有访问该模型的权限。"),
                retryable=False,
            ) from exc

        except BadRequestError as exc:
            raise ModelClientError(
                code="BAD_REQUEST",
                message=("模型请求格式错误，请检查消息或工具定义。"),
                retryable=False,
            ) from exc

        except RateLimitError as exc:
            raise ModelClientError(
                code="RATE_LIMIT",
                message=("模型服务请求过于频繁，请稍后重试。"),
                retryable=True,
            ) from exc

        except APITimeoutError as exc:
            raise ModelClientError(
                code="TIMEOUT",
                message="模型服务响应超时，请稍后重试。",
                retryable=True,
            ) from exc

        except APIConnectionError as exc:
            raise ModelClientError(
                code="CONNECTION_ERROR",
                message="无法连接模型服务，请检查网络。",
                retryable=True,
            ) from exc

        except APIStatusError as exc:
            raise ModelClientError(
                code="API_STATUS_ERROR",
                message=(f"模型服务返回异常状态：{exc.status_code}"),
                retryable=exc.status_code >= 500,
            ) from exc
