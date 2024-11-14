########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from fastapi import FastAPI

from app.healthcheck import healthcheck_router
from app.dialog import dialog_router


app = FastAPI()

app.include_router(router=healthcheck_router, prefix='/api')
app.include_router(router=dialog_router, prefix='/api')

