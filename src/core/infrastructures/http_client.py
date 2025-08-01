import ssl
import typing

import httpx
from httpx import AsyncBaseTransport, URL
from httpx._client import EventHook
from httpx._config import DEFAULT_TIMEOUT_CONFIG, Limits, DEFAULT_LIMITS, DEFAULT_MAX_REDIRECTS
from httpx._types import AuthTypes, QueryParamTypes, HeaderTypes, CookieTypes, CertTypes, ProxyTypes, TimeoutTypes


class HttpClient:
    async def __call__(
            self,
            *,
            auth: AuthTypes | None = None,
            params: QueryParamTypes | None = None,
            headers: HeaderTypes | None = None,
            cookies: CookieTypes | None = None,
            verify: ssl.SSLContext | str | bool = True,
            cert: CertTypes | None = None,
            http1: bool = True,
            http2: bool = False,
            proxy: ProxyTypes | None = None,
            mounts: typing.Mapping[str, AsyncBaseTransport | None] | None = None,
            timeout: TimeoutTypes = DEFAULT_TIMEOUT_CONFIG,
            follow_redirects: bool = False,
            limits: Limits = DEFAULT_LIMITS,
            max_redirects: int = DEFAULT_MAX_REDIRECTS,
            event_hooks: (typing.Mapping[str, list[EventHook]]) | None = None,
            base_url: URL | str = "",
            transport: AsyncBaseTransport | None = None,
            trust_env: bool = True,
            default_encoding: str | typing.Callable[[bytes], str] = "utf-8"
    ):
        async def wrapper():
            async with httpx.AsyncClient(
                    auth=auth,
                    params=params,
                    headers=headers,
                    cookies=cookies,
                    verify=verify,
                    cert=cert,
                    http1=http1,
                    http2=http2,
                    proxy=proxy,
                    mounts=mounts,
                    timeout=timeout,
                    follow_redirects=follow_redirects,
                    limits=limits,
                    max_redirects=max_redirects,
                    event_hooks=event_hooks,
                    base_url=base_url,
                    transport=transport,
                    trust_env=trust_env,
                    default_encoding=default_encoding,
            ) as client:
                yield client
        return wrapper
