from typing import Optional
from pydantic import BaseModel

from services.enel_service.common.db_schemes import ApplicationExecutionModel


class ApplicationSubmissionResponse(BaseModel):
    db_entry: ApplicationExecutionModel
    template_code: Optional[list] = []
    k8s_api_response: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "db_entry": {},
                "template_code": [],
                "k8s_api_response": {}
            }
        }
