
#!/usr/bin/env python3

import json


def test_api_format():
    """Test the API with different request formats."""

    # Use a placeholder instead of a real HubSpot API token.
    test_token = "YOUR_HUBSPOT_PRIVATE_APP_ACCESS_TOKEN"

    # Test with the legacy format
    legacy_payload = {
        "connection_id": "123e4567-e89b-12d3-a456-426612264100",
        "token": test_token,
        "config": {
            "extract_companies": True,
            "extract_deals": True,
            "extract_pipelines": True,
            "batch_size": 100
        }
    }

    # Test with the new format
    new_payload = {
        "config": {
            "scanId": "123e4567-e89b-12d3-a456-426612264100",
            "auth": {
                "accessToken": test_token
            },
            "type": ["companies", "deals", "pipelines"],
            "extraction": {
                "batch_size": 100
            }
        }
    }

    print("Testing legacy format:")
    print(json.dumps(legacy_payload, indent=2))

    print("\nTesting new format:")
    print(json.dumps(new_payload, indent=2))


if __name__ == "__main__":
    test_api_format()
