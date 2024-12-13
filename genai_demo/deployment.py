########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from aws_cdk import Stack
from constructs import Construct

from genai_demo.network.networking import Network 
from genai_demo.applications.orchestration import ECS
from genai_demo.applications.frontend import Frontend
from genai_demo.applications.backend import Backend


SOURCE_REPO_NAME = 'GenAIDemo'
BUILD_PROJECT_NAME = 'GenAI-Build-Image'
VPC_CIDR = '10.0.0.0/16'


class GenAIDemo(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        ##########################################################
        # Application Deployment
        ##########################################################
        networking = Network(
            self,
            'Networking',
            cidr=VPC_CIDR
        )

        ecs = ECS(
            self,
            'Containers',
            vpc=networking.vpc
        )
        ecs.node.add_dependency(networking)

        ##########################################################
        # Client and Server Mode
        ##########################################################
        backend_app = Backend(
            self,
            'BackendApp',
            cluster=ecs.cluster,
            container_log_group=ecs.container_log_group,
            build_image_def_log_group=ecs.build_image_def_log_group,
            sg=networking.backend_sg
        )   

        ##########################################################
        # Client Mode
        ##########################################################
        frontend_app = Frontend(
            self,
            'FrontendApp',
            cluster=ecs.cluster,
            alb=networking.alb,
            container_log_group=ecs.container_log_group,
            build_image_def_log_group=ecs.build_image_def_log_group,
            sg=networking.frontend_sg
        )
