"""Lambda Handler"""
import logging
from typing import Any

from .doc_process import DocumentProcess
from .doc_process import ResolveMedia
from .formatters import MediaResponse
from .media import LambdaEvent
from .meta_proc import MetaProcess
from .s3_proc import S3Process
from .sync_sub import Sync


def lambda_handler(event: LambdaEvent, _context: Any) -> dict[Any, Any]:
    """Media Microservice Lambda Handler"""
    method = event["requestContext"]["http"]["method"]

    # Start Log
    logging.debug("checking log")
    try:
        match (method):
            case "POST":

                sync_proc: Sync = Sync().add(S3Process).add(MetaProcess).add(DocumentProcess)

                result = sync_proc.execute(event)

                body = MediaResponse.format(result)

                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": body,
                }

            case "GET":
                sync_proc = Sync().add(ResolveMedia)

                resolved_media: dict[str, Any] = sync_proc.execute(event)
                status = 200
                if resolved_media['data'] is False:
                    status = 409
                    body = {"message": "Unable to resolve media."}
                elif len(resolved_media['data']):
                    status = 404
                    body = {"message": "Unable to locate media."}
                else:
                    body = resolved_media
                return {
                    "statusCode": status,
                    "headers": {
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": body,
                }
            case _:
                return {"statusCode": 405, "body": {"message": f"{method} Not Allowed."}}
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "body": {'message': f"{e}"},
        }
