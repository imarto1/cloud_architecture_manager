from aws_parser.models import Architecture, Relationship, Resource, Tag


def test_architecture_model_round_trip() -> None:
    architecture = Architecture(
        name="Production VPC",
        description="Main production network architecture",
        resources=[
            Resource(
                id="arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
                name="web-parsing_service-01",
                type="aws_instance",
                region="us-east-1",
                account_id="123456789012",
                tags=[Tag(key="Environment", value="Production")],
                metadata={"InstanceType": "t3.medium", "State": "running"},
            ),
            Resource(
                id="arn:aws:s3:::my-secure-bucket",
                name="my-secure-bucket",
                type="aws_s3_bucket",
                region="us-east-1",
                account_id="123456789012",
            ),
        ],
        relationships=[
            Relationship(
                source_id="arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
                target_id="arn:aws:s3:::my-secure-bucket",
                relationship_type="accesses",
                metadata={"permission": "read-write"},
            )
        ],
    )

    data = architecture.model_dump()

    restored = Architecture.model_validate(data)
    assert restored.name == "Production VPC"
    assert len(restored.resources) == 2
    assert restored.resources[0].tags[0].key == "Environment"
    assert restored.relationships[0].relationship_type == "accesses"
