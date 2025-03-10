from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
import requests
import os
import json

router = APIRouter()
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
REDIRECT_URI = os.getenv("WECHAT_CALL_BACK_URL")


@router.get("/api/auth/wechat")
def wechat_auth():
    auth_url = f"https://open.weixin.qq.com/connect/qrconnect?appid={APP_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect"
    return JSONResponse({"url": auth_url})


@router.get("/auth/wechat/callback")
async def wechat_callback(code: str):
    """Handle WeChat OAuth callback"""
    if not code:
        return JSONResponse(
            {"error": "Authorization failed: No code provided."}, status_code=400
        )

    try:
        # Exchange code for access token
        token_response = requests.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": APP_ID,
                "secret": APP_SECRET,
                "code": code,
                "grant_type": "authorization_code",
            },
        ).json()

        access_token = token_response.get("access_token")
        openid = token_response.get("openid")

        if not access_token or not openid:
            return JSONResponse(
                {"error": "Failed to get access token."}, status_code=401
            )

        # Fetch user info
        user_info = requests.get(
            "https://api.weixin.qq.com/sns/userinfo",
            params={"access_token": access_token, "openid": openid},
        ).json()

        print(f"user_info: {user_info}")
        nickname = user_info["nickname"].encode("latin-1").decode("utf-8")
        print(nickname)
        user_info["nickname"] = nickname
        # Return success with postMessage to parent window
        html_response = (
            """
            <script>
                window.opener.postMessage(
                    { type: 'wechat-login-success', user: %s },
                    '*'
                );
                window.close();
            </script>
        """
            % user_info
        )

        return HTMLResponse(content=html_response)

    except Exception as e:
        return JSONResponse({"error": f"Login failed: {str(e)}"}, status_code=500)
