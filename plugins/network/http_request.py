import requests
import httpx
import asyncio
from agent.rpc_registry import register_method

# 同步 GET 请求
@register_method(
    "network.http.get",
    param_desc={
        "url": "请求的 URL，字符串",
        "params": "请求参数，字典，可选",
        "headers": "请求头，字典，可选"
    },
    description="同步 GET 请求"
)
def http_get(url, params=None, headers=None):
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
        }
    except Exception as e:
        return {"error": str(e)}

# 同步 POST 请求
@register_method(
    "network.http.post",
    param_desc={
        "url": "请求的 URL，字符串",
        "data": "请求体数据，字典或字符串",
        "headers": "请求头，字典，可选"
    },
    description="同步 POST 请求"
)
def http_post(url, data=None, headers=None):
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "text": response.text,
        }
    except Exception as e:
        return {"error": str(e)}

# 异步 GET 请求
@register_method(
    "network.http.async_get",
    param_desc={
        "url": "请求的 URL，字符串",
        "params": "请求参数，字典，可选",
        "headers": "请求头，字典，可选"
    },
    description="异步 GET 请求"
)
async def async_http_get(url, params=None, headers=None):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, params=params, headers=headers)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "text": response.text,
            }
        except Exception as e:
            return {"error": str(e)}

# 异步 POST 请求
@register_method(
    "network.http.async_post",
    param_desc={
        "url": "请求的 URL，字符串",
        "data": "请求体数据，字典或字符串",
        "headers": "请求头，字典，可选"
    },
    description="异步 POST 请求"
)
async def async_http_post(url, data=None, headers=None):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(url, json=data, headers=headers)
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "text": response.text,
            }
        except Exception as e:
            return {"error": str(e)}
