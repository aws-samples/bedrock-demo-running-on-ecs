########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from aws_cdk import (
    RemovalPolicy, Duration, Size,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_s3 as s3,
    aws_ecr_assets as ecr_assets,
    aws_logs as logs,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
)
from constructs import Construct
from cdk_ecr_deployment import DockerImageName, ECRDeployment


class Backend(Construct):

    def __init__(self, scope: Construct, id_: str, cluster: ecs.Cluster, sg: ec2.SecurityGroup,
                 container_log_group: logs.LogGroup, build_image_def_log_group: logs.LogGroup) -> None:
        super().__init__(scope, id_)

        name = 'backend-app'

        # Backend Repo
        self.ecr_repo = ecr.Repository(
            self,
            'BackendRepo',
            repository_name=name,
            removal_policy=RemovalPolicy.DESTROY,
            empty_on_delete=True
        )

        image_asset = ecr_assets.DockerImageAsset(
            self,
            'BackendAppDockerImage',
            directory='src/apps/backend/',
            platform=ecr_assets.Platform.LINUX_AMD64
        )
        image_asset.node.add_dependency(self.ecr_repo)

        ecr_deployment = ECRDeployment(
            self,
            'DeployBackendAppImage',
            src=DockerImageName(image_asset.image_uri),
            dest=DockerImageName(
                f'{self.ecr_repo.repository_uri}:latest'
            )
        )
        ecr_deployment.node.add_dependency(image_asset)        

        # ECS Task Definition
        task_def = ecs.FargateTaskDefinition(
            self,
            'BackendAppTaskDef',
            cpu=512,
            memory_limit_mib=1024,
            family='BackendAppTaskDef'
        )
        
        # Task Role
        task_def.add_to_task_role_policy(
            statement=iam.PolicyStatement(
                actions=[
                    'bedrock:InvokeModel',
                    'bedrock:InvokeModelWithResponseStream'
                ],
                resources=[
                    'arn:aws:bedrock:*::foundation-model/*',
                ],
                effect=iam.Effect.ALLOW
            )
        )

        task_def.add_to_task_role_policy(
            statement=iam.PolicyStatement(
                actions=[
                    'logs:CreateLogGroup',
                    'logs:CreateLogStream',
                    'logs:PutLogEvents'
                ],
                resources=[
                    '*'
                ],
                effect=iam.Effect.ALLOW
            )                    
        )

        # For HealthCheck, Don't need to set Container's health check, if ALB's health check is enabled.
        # https://repost.aws/questions/QUdmR0oMn2Spa61RpKGWyPfg/ecs-should-i-use-alb-healthchecks-container-healthchecks-or-both
        task_def.add_container(
            'BackendApp',
            container_name=name,
            image=ecs.ContainerImage.from_ecr_repository(
                self.ecr_repo,
                tag='latest'
            ),
            port_mappings=[
                ecs.PortMapping(
                    name='backend',
                    container_port=8080,
                    host_port=8080,
                    protocol=ecs.Protocol.TCP,
                    app_protocol=ecs.AppProtocol.http
                )
            ],
            logging=ecs.LogDrivers.aws_logs(
                log_group=container_log_group,
                stream_prefix='service',
                mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                max_buffer_size=Size.mebibytes(25)
            )
        )

        service = ecs.FargateService(
            self,
            'BackendAppService',
            service_name='BackendAppService',
            cluster=cluster,
            task_definition=task_def,
            desired_count=2,
            deployment_controller=ecs.DeploymentController(
                type=ecs.DeploymentControllerType.ECS
            ),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[sg],
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(
                    capacity_provider='FARGATE_SPOT',
                    weight=2
                ),
                ecs.CapacityProviderStrategy(
                    capacity_provider='FARGATE',
                    weight=1
                )
            ],
            service_connect_configuration=ecs.ServiceConnectProps(
                log_driver=ecs.LogDrivers.aws_logs(
                    log_group=container_log_group,
                    stream_prefix='sc-backend',
                    mode=ecs.AwsLogDriverMode.NON_BLOCKING,
                    max_buffer_size=Size.mebibytes(25)
                ),
                services=[
                    ecs.ServiceConnectService(
                        port_mapping_name='backend',
                        port=8080,
                        idle_timeout=Duration.minutes(10),
                        per_request_timeout=Duration.minutes(5)
                    )
                ]
            ),
            circuit_breaker=ecs.DeploymentCircuitBreaker(
                enable=True,
                rollback=True
            )
        )

        # Task Autoscaling
        scaling = service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=10
        )

        scaling.scale_on_memory_utilization(
            'MemoryScaling',
            policy_name='MemoryScaling',
            target_utilization_percent=70
        )

        # CI/CD
        artifact_bucket = s3.Bucket(
            self,
            'ArtifactBucket',
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True, 
            enforce_ssl=True
        )

        pipeline = codepipeline.Pipeline(
            self,
            'BackendAppPipeline',
            pipeline_name='BackendAppPipeline',
            pipeline_type=codepipeline.PipelineType.V2,
            artifact_bucket=artifact_bucket
        )

        # Source Stage
        source_output = codepipeline.Artifact(artifact_name='Source')
        source_action = codepipeline_actions.EcrSourceAction(
            action_name='Source',
            repository=self.ecr_repo,
            image_tag='latest',
            output=source_output
        )
        pipeline.add_stage(
            stage_name='Source',
            actions=[source_action]
        )

        # Build Stage
        image_def_builder = codebuild.Project(
            self,
            'ImageDefBuild',
            project_name='GenAI-Backend-Build-Image-Definition',
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_5,
            ),
            build_spec=codebuild.BuildSpec.from_asset(
                path='genai_demo/applications/buildspec.yml'
            ),
            logging=codebuild.LoggingOptions(
                cloud_watch=codebuild.CloudWatchLoggingOptions(
                    enabled=True,
                    log_group=build_image_def_log_group,
                    prefix='backend'
                )
            )
        )

        build_output = codepipeline.Artifact(artifact_name='Build')
        build_action = codepipeline_actions.CodeBuildAction(
            action_name='Build',
            project=image_def_builder,
            input=source_output,
            outputs=[build_output],
            environment_variables={
                'ContainerName': codebuild.BuildEnvironmentVariable(value=name)
            }
        )
        pipeline.add_stage(
            stage_name='Build',
            actions=[build_action]
        )

        # Deploy Stage
        deploy_action = codepipeline_actions.EcsDeployAction(
            action_name='Deploy',
            service=service,
            input=build_output
        )

        pipeline.add_stage(
            stage_name='Deploy',
            actions=[deploy_action]
        )
