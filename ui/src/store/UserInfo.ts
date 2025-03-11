import { defineStore } from "pinia";
import { useSystemConfig } from "./Config";

interface UserState {
  isAuthenticated: boolean;
  userInfo: any | null;
  sessionId: string | undefined;
}

export const useUserInfo = defineStore("user-info", {
  state: (): UserState => ({
    isAuthenticated: false,
    userInfo: null,
    sessionId: undefined,
  }),
  actions: {
    async login() {
      try {
        const config = useSystemConfig();
        const authResponse = await fetch(config.getURL("/api/auth/wechat"));
        if (!authResponse.ok) {
          throw new Error("Failed to get WeChat auth URL");
        }

        const { url } = await authResponse.json();
        const width = 600;
        const height = 600;
        const left = window.screenX + (window.outerWidth - width) / 2;
        const top = window.screenY + (window.outerHeight - height) / 2;

        const loginWindow = window.open(
          url,
          "WeChatLogin",
          `width=${width},height=${height},left=${left},top=${top}`
        );

        return new Promise((resolve) => {
          window.addEventListener("message", async (event) => {
            if (event.data.type === "wechat-login-success") {
              loginWindow?.close();
              this.isAuthenticated = true;
              this.userInfo = event.data.user;
              this.sessionId = event.data.session_id;
              resolve(event.data.user);
            }
          });
        });
      } catch (error) {
        console.error("WeChat login failed:", error);
        throw error;
      }
    },

    async checkLoginStatus() {
      try {
        const response = await fetch("/api/auth/status");
        const data = await response.json();

        if (data.authenticated) {
          return true;
        }

        this.sessionId = undefined;
        return false;
      } catch (error) {
        console.error("Failed to check login status:", error);
        return false;
      }
    },

    async logout() {
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
        });
        this.isAuthenticated = false;
        this.userInfo = null;
        this.sessionId = undefined;
      } catch (error) {
        console.error("Logout failed:", error);
        throw error;
      }
    },
  },
});
