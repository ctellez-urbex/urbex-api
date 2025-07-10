#!/usr/bin/env python3
"""
Script to fetch CloudWatch logs for the Lambda function.
"""

import json
import os
from datetime import datetime, timedelta

import boto3


def get_cloudwatch_logs():
    """Get CloudWatch logs for the Lambda function."""

    # AWS clients
    logs_client = boto3.client("logs", region_name="us-east-2")

    # Log group name
    log_group_name = "/aws/lambda/urbex-api-prod-api"

    print(f"🔍 Fetching logs from: {log_group_name}")

    try:
        # Get recent log streams
        response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
            maxItems=5,
        )

        print(f"📋 Found {len(response['logStreams'])} log streams")

        for i, stream in enumerate(response["logStreams"]):
            print(f"\n📄 Log Stream {i+1}: {stream['logStreamName']}")
            print(
                f"   Last Event Time: {datetime.fromtimestamp(stream['lastEventTimestamp']/1000)}"
            )

            # Get events from this stream
            events_response = logs_client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=stream["logStreamName"],
                startTime=int((datetime.now() - timedelta(hours=1)).timestamp() * 1000),
                limit=50,
            )

            print(f"   Events found: {len(events_response['events'])}")

            # Filter for relevant logs
            relevant_logs = []
            for event in events_response["events"]:
                message = event["message"]
                if any(
                    keyword in message
                    for keyword in [
                        "🔍",
                        "❌",
                        "⚠️",
                        "✅",
                        "Processing attribute",
                        "custom:su",
                        "Admin user info",
                        "Basic user info",
                        "Failed to get user",
                    ]
                ):
                    relevant_logs.append(
                        {
                            "timestamp": datetime.fromtimestamp(
                                event["timestamp"] / 1000
                            ),
                            "message": message,
                        }
                    )

            if relevant_logs:
                print(f"   Relevant logs found: {len(relevant_logs)}")
                for log in relevant_logs[-10:]:  # Show last 10 relevant logs
                    print(f"   [{log['timestamp']}] {log['message']}")
            else:
                print("   No relevant logs found in this stream")

    except Exception as e:
        print(f"❌ Error fetching logs: {e}")
        print("Make sure you have AWS credentials configured and proper permissions")


def get_recent_logs_simple():
    """Get recent logs using a simpler approach."""

    logs_client = boto3.client("logs", region_name="us-east-2")
    log_group_name = "/aws/lambda/urbex-api-prod-api"

    try:
        # Get logs from the last hour
        start_time = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)

        # First, try without filter pattern
        response = logs_client.filter_log_events(
            logGroupName=log_group_name, startTime=start_time, limit=10
        )

        print(f"🔍 Found {len(response['events'])} total log events")
        print("=" * 80)

        for event in response["events"]:
            timestamp = datetime.fromtimestamp(event["timestamp"] / 1000)
            message = event["message"]
            print(f"[{timestamp}] {message}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error details: {type(e).__name__}")


if __name__ == "__main__":
    print("🔍 CloudWatch Logs Analysis")
    print("=" * 50)

    # Try simple approach first
    get_recent_logs_simple()
