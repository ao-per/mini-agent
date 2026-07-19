from abc import ABC, abstractmethod
from typing import Any, ClassVar

from pydantic import BaseModel


class Tool(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    args_model: ClassVar[type[BaseModel]]

    def schema(self) -> dict[str, Any]:
        """生成可传给 Responses API 的工具定义。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            },
        }

    @abstractmethod
    def run(self, arguments: BaseModel) -> Any:
        """执行工具。"""
        raise NotImplementedError
