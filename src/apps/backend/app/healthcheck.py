########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from fastapi import status, APIRouter
from pydantic import BaseModel

healthcheck_router = APIRouter()

class HealthCheck(BaseModel):
    status: str


@healthcheck_router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck
)
def get_health() -> HealthCheck:
    return HealthCheck(status='OK')
