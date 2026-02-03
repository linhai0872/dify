# [CUSTOM] 二开: Service API 远程文件操作接口
# 业务价值: 业务系统通过 URL 直接导入文件到 Dify
import urllib.parse

import httpx
from flask_restx import Resource
from flask_restx.api import HTTPStatus
from pydantic import BaseModel, Field, HttpUrl

import services
from controllers.common import helpers
from controllers.common.errors import (
    FileTooLargeError,
    RemoteFileUploadError,
    UnsupportedFileTypeError,
)
from controllers.common.schema import register_schema_models
from controllers.service_api import service_api_ns
from controllers.service_api.wraps import FetchUserArg, WhereisUserArg, validate_app_token
from core.file import helpers as file_helpers
from core.helper import ssrf_proxy
from extensions.ext_database import db
from fields.file_fields import FileWithSignedUrl, RemoteFileInfo
from models import App, EndUser
from services.file_service import FileService


class CustomRemoteFileUploadPayload(BaseModel):
    url: HttpUrl = Field(description="Remote file URL")


register_schema_models(service_api_ns, CustomRemoteFileUploadPayload, RemoteFileInfo, FileWithSignedUrl)


@service_api_ns.route("/custom/remote-files/<path:url>")
class CustomRemoteFileInfoApi(Resource):
    """获取远程文件元信息接口"""

    @service_api_ns.doc("get_custom_remote_file_info")
    @service_api_ns.doc(description="Get information about a remote file through SSRF protection proxy")
    @service_api_ns.doc(
        responses={
            200: "Remote file information retrieved successfully",
            400: "Bad request - invalid URL or failed to fetch",
            401: "Unauthorized - invalid API token",
            500: "Failed to fetch remote file",
        }
    )
    @validate_app_token()
    @service_api_ns.response(HTTPStatus.OK, "Remote file info", service_api_ns.models[RemoteFileInfo.__name__])
    def get(self, app_model: App, url: str):
        """Get information about a remote file.

        Retrieves basic information about a file located at a remote URL,
        including content type and content length.

        Args:
            app_model: The associated application model
            url: URL-encoded path to the remote file

        Returns:
            dict: Remote file information including type and length

        Raises:
            RemoteFileUploadError: If the remote file cannot be accessed
        """
        decoded_url = urllib.parse.unquote(url)

        try:
            resp = ssrf_proxy.head(decoded_url)
            if resp.status_code != httpx.codes.OK:
                # Fall back to GET method if HEAD fails
                resp = ssrf_proxy.get(decoded_url, timeout=3)
            resp.raise_for_status()
        except httpx.RequestError as e:
            raise RemoteFileUploadError(f"Failed to fetch file from {decoded_url}: {e!s}")

        info = RemoteFileInfo(
            file_type=resp.headers.get("Content-Type", "application/octet-stream"),
            file_length=int(resp.headers.get("Content-Length", -1)),
        )
        return info.model_dump(mode="json")


@service_api_ns.route("/custom/remote-files/upload")
class CustomRemoteFileUploadApi(Resource):
    """远程文件上传接口"""

    @service_api_ns.doc("upload_custom_remote_file")
    @service_api_ns.doc(description="Download a file from a remote URL and upload it to Dify storage")
    @service_api_ns.doc(
        responses={
            201: "Remote file uploaded successfully",
            400: "Bad request - invalid URL or parameters",
            401: "Unauthorized - invalid API token",
            413: "File too large",
            415: "Unsupported file type",
            500: "Failed to fetch remote file",
        }
    )
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON))
    @service_api_ns.expect(service_api_ns.models[CustomRemoteFileUploadPayload.__name__])
    @service_api_ns.response(
        HTTPStatus.CREATED, "Remote file uploaded", service_api_ns.models[FileWithSignedUrl.__name__]
    )
    def post(self, app_model: App, end_user: EndUser):
        """Upload a file from a remote URL.

        Downloads a file from the provided remote URL and uploads it
        to the platform storage for use in applications.

        Args:
            app_model: The associated application model
            end_user: The end user making the request

        JSON Parameters:
            url: The remote URL to download the file from (required)

        Returns:
            dict: File information including ID, signed URL, and metadata
            int: HTTP status code 201 for success

        Raises:
            RemoteFileUploadError: Failed to fetch file from remote URL
            FileTooLargeError: File exceeds size limit
            UnsupportedFileTypeError: File type not supported
        """
        payload = CustomRemoteFileUploadPayload.model_validate(service_api_ns.payload or {})
        url = str(payload.url)

        try:
            resp = ssrf_proxy.head(url=url)
            if resp.status_code != httpx.codes.OK:
                resp = ssrf_proxy.get(url=url, timeout=3, follow_redirects=True)
            if resp.status_code != httpx.codes.OK:
                raise RemoteFileUploadError(f"Failed to fetch file from {url}: {resp.text}")
        except httpx.RequestError as e:
            raise RemoteFileUploadError(f"Failed to fetch file from {url}: {e!s}")

        file_info = helpers.guess_file_info_from_response(resp)

        if not FileService.is_file_size_within_limit(extension=file_info.extension, file_size=file_info.size):
            raise FileTooLargeError

        content = resp.content if resp.request.method == "GET" else ssrf_proxy.get(url).content

        try:
            upload_file = FileService(db.engine).upload_file(
                filename=file_info.filename,
                content=content,
                mimetype=file_info.mimetype,
                user=end_user,
                source_url=url,
            )
        except services.errors.file.FileTooLargeError as file_too_large_error:
            raise FileTooLargeError(file_too_large_error.description)
        except services.errors.file.UnsupportedFileTypeError:
            raise UnsupportedFileTypeError()

        response_payload = FileWithSignedUrl(
            id=upload_file.id,
            name=upload_file.name,
            size=upload_file.size,
            extension=upload_file.extension,
            url=file_helpers.get_signed_file_url(upload_file_id=upload_file.id),
            mime_type=upload_file.mime_type,
            created_by=upload_file.created_by,
            created_at=int(upload_file.created_at.timestamp()),
        )
        return response_payload.model_dump(mode="json"), 201


# [/CUSTOM]
