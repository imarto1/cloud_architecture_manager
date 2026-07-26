#!/bin/bash
set -eu

create_bucket() {
    awslocal s3 mb "s3://$1"
    awslocal s3 cp /etc/hosts "s3://$1/seed-data.txt"
}

create_table() {
    awslocal dynamodb create-table \
        --table-name "$1" \
        --key-schema AttributeName=id,KeyType=HASH \
        --attribute-definitions AttributeName=id,AttributeType=S \
        --billing-mode PAY_PER_REQUEST
}

create_instance() {
    awslocal ec2 run-instances \
        --image-id ami-12345678 \
        --count 1 \
        --instance-type t2.micro \
        --tag-specifications "ResourceType=instance,Tags=[{Key=ArchitectureId,Value=$1}]"
}

case "${ARCHITECTURE_ID:?ARCHITECTURE_ID must be set}" in
    web-application)
        create_bucket web-application-assets; create_table WebApplicationSessions; create_instance web-application ;;
    public-api)
        create_bucket public-api-documents; create_table PublicApiKeys ;;
    ecommerce)
        create_bucket ecommerce-product-media; create_table EcommerceOrders; create_instance ecommerce ;;
    real-time-analytics)
        create_bucket real-time-analytics-lake; create_table RealtimeAnalyticsState ;;
    batch-processing)
        create_bucket batch-processing-input; create_instance batch-processing ;;
    event-processing)
        create_table EventProcessingState; awslocal sqs create-queue --queue-name event-processing-events ;;
    media-delivery)
        create_bucket media-delivery-content ;;
    internal-tool)
        create_table InternalToolData; create_instance internal-tool ;;
    iot-ingestion)
        create_bucket iot-ingestion-raw; create_table IotDeviceState; awslocal sqs create-queue --queue-name iot-ingestion-messages ;;
    ml-inference)
        create_bucket ml-inference-models; create_table MlInferenceRequests; create_instance ml-inference ;;
    *)
        echo "Unknown architecture: $ARCHITECTURE_ID" >&2; exit 1 ;;
esac

echo "LocalStack initialized $ARCHITECTURE_ID cloud."
