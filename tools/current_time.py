from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from tools.base import Tool


class CurrentTimeArgs(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )

    timezone: str = Field(
        description=(
            "IANA timezone name, for example Asia/Shanghai or America/New_York."
        )
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {value}") from exc

        return value


class CurrentTimeTool(Tool):
    name = "current_time"
    description = "Get the current date and time in a specified timezone."
    args_model = CurrentTimeArgs

    def run(self, arguments: BaseModel) -> str:
        if not isinstance(arguments, CurrentTimeArgs):
            raise TypeError("Expected CurrentTimeArgs")

        timezone = ZoneInfo(arguments.timezone)
        current_time = datetime.now(timezone)

        return current_time.isoformat(timespec="seconds")
