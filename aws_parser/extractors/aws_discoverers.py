"""Service-specific AWS resource adapters used by the generic scanner."""

from __future__ import annotations

from typing import Any, Protocol

from aws_parser.DTOs.architecture import Resource


class ResourceDiscoverer(Protocol):
    service: str

    def discover(self, client: Any, region: str) -> list[Resource]: ...


class S3Discoverer:
    service = "s3"

    def discover(self, client: Any, region: str) -> list[Resource]:
        return [
            Resource(
                id=f"arn:aws:s3:::{bucket['Name']}",
                name=bucket["Name"],
                type="aws_s3_bucket",
                region=region,
                account_id="unknown",
                metadata={"creation_date": bucket["CreationDate"].isoformat()},
            )
            for bucket in client.list_buckets()["Buckets"]
        ]


class Ec2Discoverer:
    service = "ec2"

    def discover(self, client: Any, region: str) -> list[Resource]:
        resources = []
        for reservation in client.describe_instances()["Reservations"]:
            for instance in reservation["Instances"]:
                tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                resources.append(
                    Resource(
                        id=instance["InstanceId"],
                        name=tags.get("Name") or tags.get("ArchitectureId"),
                        type="aws_ec2_instance",
                        region=region,
                        account_id="unknown",
                        metadata={
                            "state": instance["State"]["Name"],
                            "instance_type": instance["InstanceType"],
                            "vpc_id": instance.get("VpcId"),
                            "subnet_id": instance.get("SubnetId"),
                            "security_group_ids": [
                                group["GroupId"] for group in instance.get("SecurityGroups", [])
                            ],
                        },
                    )
                )
        return resources


class DynamoDbDiscoverer:
    service = "dynamodb"

    def discover(self, client: Any, region: str) -> list[Resource]:
        resources = []
        for table_name in client.list_tables()["TableNames"]:
            table = client.describe_table(TableName=table_name)["Table"]
            resources.append(
                Resource(
                    id=table["TableArn"],
                    name=table_name,
                    type="aws_dynamodb_table",
                    region=region,
                    account_id="unknown",
                    metadata={
                        "status": table["TableStatus"],
                        "key_schema": table["KeySchema"],
                        "billing_mode": table.get("BillingModeSummary", {}).get("BillingMode"),
                    },
                )
            )
        return resources


class SqsDiscoverer:
    service = "sqs"

    def discover(self, client: Any, region: str) -> list[Resource]:
        resources = []
        for queue_url in client.list_queues().get("QueueUrls", []):
            attributes = client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])["Attributes"]
            resources.append(
                Resource(
                    id=attributes["QueueArn"],
                    name=queue_url.rsplit("/", 1)[-1],
                    type="aws_sqs_queue",
                    region=region,
                    account_id="unknown",
                    metadata={"queue_url": queue_url},
                )
            )
        return resources


class IamDiscoverer:
    service = "iam"

    def discover(self, client: Any, region: str) -> list[Resource]:
        return [
            Resource(
                id=role["Arn"],
                name=role["RoleName"],
                type="aws_iam_role",
                region="global",
                account_id="unknown",
                metadata={
                    "path": role["Path"],
                    "create_date": role["CreateDate"].isoformat(),
                },
            )
            for page in client.get_paginator("list_roles").paginate()
            for role in page["Roles"]
        ]


class KinesisDiscoverer:
    service = "kinesis"

    def discover(self, client: Any, region: str) -> list[Resource]:
        resources = []
        for page in client.get_paginator("list_streams").paginate():
            for stream_name in page["StreamNames"]:
                stream = client.describe_stream_summary(StreamName=stream_name)["StreamDescriptionSummary"]
                resources.append(
                    Resource(
                        id=stream["StreamARN"],
                        name=stream_name,
                        type="aws_kinesis_stream",
                        region=region,
                        account_id="unknown",
                        metadata={
                            "status": stream["StreamStatus"],
                            "retention_period_hours": stream["RetentionPeriodHours"],
                            "open_shards": stream["OpenShardCount"],
                        },
                    )
                )
        return resources


DEFAULT_DISCOVERERS: dict[str, ResourceDiscoverer] = {
    discoverer.service: discoverer
    for discoverer in (
        S3Discoverer(),
        Ec2Discoverer(),
        DynamoDbDiscoverer(),
        SqsDiscoverer(),
        IamDiscoverer(),
        KinesisDiscoverer(),
    )
}
