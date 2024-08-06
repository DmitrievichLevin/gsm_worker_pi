"""Lambda Handler"""
from typing import Any

from .doc_process import DocumentProcess
from .doc_process import ResolveMedia
from .formatters import DocumentResponse
from .formatters import MediaResponse
from .media import LambdaEvent
from .meta_proc import MetaDelete
from .meta_proc import MetaProcess
from .s3_proc import S3Delete
from .s3_proc import S3Process
from .sync_sub import Sync


def lambda_handler(event: LambdaEvent, _context: Any) -> dict[Any, Any]:
    """Media Microservice Lambda Handler"""
    method = event["requestContext"]["http"]["method"]

    try:
        match (method):
            case "POST":

                post_proc: Sync = Sync().add(S3Process).add(MetaProcess).add(DocumentProcess)

                result = post_proc.execute(event)

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
                get_proc = Sync().add(ResolveMedia)

                resolved_media: dict[str, Any] = get_proc.execute(event)
                status = 200
                if resolved_media['data'] is False:
                    status = 409
                    body = {"message": "Unable to resolve media."}
                elif len(resolved_media['data']) == 0:
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
            case "DELETE":
                get_proc = Sync().add(DocumentProcess).add(S3Delete).add(MetaDelete)

                # Result of sync process
                result = get_proc.execute(event)

                # Get Removed Media Id's from Process
                deleted_media_ids = result['deleted']

                # Get updated doc from result
                updated_doc = result['updated_doc']

                return {
                    "statusCode": 200,
                    "headers": {
                        "Access-Control-Allow-Headers": "Content-Type",
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                    },
                    "body": {'deleted_media': deleted_media_ids, 'updated_document': DocumentResponse.format(updated_doc)},
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
