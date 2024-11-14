########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

from aws_cdk import (
    CfnOutput,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_route53_targets as targets,
)
from constructs import Construct


class Network(Construct):

    def __init__(self, scope: Construct, id_: str, cidr: str) -> None:
        super().__init__(scope, id_)

        # VPC
        self.vpc = ec2.Vpc(
            self,
            'GenAIDemoVPC',
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='Private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ],
            nat_gateways=3,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=3,
            restrict_default_security_group=False
        )

        # ALB Security Group
        alb_sg = ec2.SecurityGroup(
            self,
            'AppicationLoadbalancerSG',
            vpc=self.vpc,
            allow_all_outbound=False,
            security_group_name='GenAIDemo-ALB-SG',
            description='GenAIDemo/ALB/SecurityGroup'
        )

        alb_sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443)
        )

        alb_sg.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443) 
        )

        # Frontend Security Group
        self.frontend_sg = ec2.SecurityGroup(
            self,
            'FrontendServiceSG',
            vpc=self.vpc,
            allow_all_outbound=True,
            security_group_name='GenAIDemo-FrontendService-SG',
            description='GenAIDemo/FrontendService/SecurityGroup'
        )        

        self.frontend_sg.add_ingress_rule(
            peer=alb_sg,
            connection=ec2.Port.tcp(8501)
        )

        # Backend Security Group
        self.backend_sg = ec2.SecurityGroup(
            self,
            'BackendServiceSG',
            vpc=self.vpc,
            allow_all_outbound=True,
            security_group_name='GenAIDemo-BackendService-SG',
            description='GenAIDemo/BackendService/SecurityGroup'
        )

        self.backend_sg.add_ingress_rule(
            peer=self.frontend_sg,
            connection=ec2.Port.tcp(8080)
        )

        # ALB
        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "GenAIDemoALB",
            load_balancer_name='genai-demo-alb',
            internet_facing=True,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            security_group=alb_sg,
            cross_zone_enabled=True
        )
