"""Lambda Handler"""

from typing import Any
from media_microservice import Sync, LambdaEvent, S3_Process, Meta_Process


def lambda_handler(event: LambdaEvent, _context: Any) -> dict[Any, Any]:
    """Media Microservice Lambda Handler"""

    method = event["requestContext"]["http"]["method"]

    match(method):
        case "POST":
            sync_proc: Sync = Sync().add(S3_Process).add(Meta_Process)

            result = sync_proc.execute(event)

            body = {"url": result['image_url'],
                    "thumbnail": result['thumb_url'],
                    "metadata": result['metadata']
                    }

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": body,
            }
        case _:
            return {
                "statusCode": 405,
                "body": {"message": f"{method} Not Allowed."}
            }
