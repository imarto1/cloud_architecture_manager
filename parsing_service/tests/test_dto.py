from parsing_service.DTOs.CloudArchitecture import CloudArchitectureDTO, AWSResourceDTO, AWSTagDTO, ResourceRelationshipDTO

def test_dto_serialization():
    # Create a sample architecture
    arch = CloudArchitectureDTO(
        name="Production VPC",
        description="Main production network architecture",
        resources=[
            AWSResourceDTO(
                id="arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
                name="web-parsing_service-01",
                type="aws_instance",
                region="us-east-1",
                account_id="123456789012",
                tags=[AWSTagDTO(key="Environment", value="Production")],
                metadata={"InstanceType": "t3.medium", "State": "running"}
            ),
            AWSResourceDTO(
                id="arn:aws:s3:::my-secure-bucket",
                name="my-secure-bucket",
                type="aws_s3_bucket",
                region="us-east-1",
                account_id="123456789012"
            )
        ],
        relationships=[
            ResourceRelationshipDTO(
                source_id="arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890",
                target_id="arn:aws:s3:::my-secure-bucket",
                relationship_type="accesses",
                metadata={"permission": "read-write"}
            )
        ]
    )

    # Serialize to dict and back to verify
    data = arch.model_dump()
    
    restored = CloudArchitectureDTO(**data)
    assert restored.name == "Production VPC"
    assert len(restored.resources) == 2
    assert restored.resources[0].tags[0].key == "Environment"
    assert restored.relationships[0].relationship_type == "accesses"
