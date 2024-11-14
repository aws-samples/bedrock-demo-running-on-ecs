#!/usr/bin/env python3
########################################################################
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
########################################################################

import os
import aws_cdk as cdk

from genai_demo.deployment import GenAIDemo
from cdk_nag import AwsSolutionsChecks, NagSuppressions


app = cdk.App()
stack = GenAIDemo(
    app,
    'GenAIDemo',
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    tags={'Project': 'genai-demo'}
)
cdk.Aspects.of(app).add(AwsSolutionsChecks())
NagSuppressions.add_stack_suppressions(stack, [
    {'id': 'AwsSolutions-CB3', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-CB4', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-IAM4', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-IAM5', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-VPC7', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-ELB2', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-EC23', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-S1', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-S10', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-ECS2', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-ECS7', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-COG1', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-COG2', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-COG3', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-SMG4', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-OS3', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-OS5', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-L1', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-EC26', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-EC28', 'reason': 'allowed in this stack'},
    {'id': 'AwsSolutions-EC29', 'reason': 'allowed in this stack'},
])
app.synth()
