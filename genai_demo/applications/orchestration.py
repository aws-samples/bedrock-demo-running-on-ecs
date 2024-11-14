########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from aws_cdk import (
    RemovalPolicy,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_logs as logs,
    aws_servicediscovery as sc
)
from constructs import Construct


class ECS(Construct):

    def __init__(self, scope: Construct, id_: str, vpc: ec2.Vpc) -> None:
        super().__init__(scope, id_)

        self.cluster = ecs.Cluster(
            self,
            'Cluster',
            cluster_name='genai-demo-cluster',
            vpc=vpc,
            container_insights=True,
            enable_fargate_capacity_providers=True,
            default_cloud_map_namespace=ecs.CloudMapNamespaceOptions(
                name='genai.demo',
                type=sc.NamespaceType.HTTP,
                use_for_service_connect=True
            )
        )

        self.container_log_group = logs.LogGroup(
            self,
            'ContainerLogGroup',
            log_group_name='/aws/ecs/GenAIDemo/containers',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )

        self.build_image_def_log_group = logs.LogGroup(
            self,
            'BuildImageDefLogGroup',
            log_group_name='/aws/codebuild/GenAIDemo/Build-Image-Definition',
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_WEEK
        )        
