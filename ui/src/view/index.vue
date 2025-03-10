<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useSystemConfig } from "../store/Config";
import { ElButton } from "element-plus";
import wechatLogo from "@/assets/images/wechat.png";

const config = useSystemConfig();
const isAuthenticated = ref<boolean>(false);
const userInfo = ref<any>(null);

const handleLogin = async () => {
  try {
    // First, get the WeChat auth URL
    const authResponse = await fetch(config.getURL("/api/auth/wechat"));
    if (!authResponse.ok) {
      throw new Error("Failed to get WeChat auth URL");
    }

    const { url } = await authResponse.json();

    // Open WeChat login in a new window
    const width = 600;
    const height = 600;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2;

    const loginWindow = window.open(
      url,
      "WeChatLogin",
      `width=${width},height=${height},left=${left},top=${top}`,
    );

    // Listen for login success message
    window.addEventListener("message", async (event) => {
      if (event.data.type === "wechat-login-success") {
        loginWindow?.close();
        isAuthenticated.value = true;
        userInfo.value = event.data.user;
      }
    });
  } catch (error) {
    console.error("WeChat login failed:", error);
  }
};
const router = useRouter();
</script>

<template>
  <div style="text-align: center">
    <div v-if="!isAuthenticated">
      <el-card class="login-box">
        <h2>微信登录</h2>
        <img
          :src="wechatLogo"
          class="wechat-logo"
          @click="handleLogin"
          alt="WeChat Login"
        />
      </el-card>
    </div>
    <div v-else>
      <el-card class="select-box">
        <h2>你好, {{ userInfo?.nickname }}. 请选择采访模式</h2>
        <el-button
          class="form-button"
          @click="router.push(`/manual/${userInfo.openid}`)"
          >manual</el-button
        >
        <el-button
          class="form-button"
          @click="router.push(`/auto/${userInfo.openid}`)"
          >auto</el-button
        >
      </el-card>
    </div>
  </div>
</template>

<style lang="css" scoped>
.login-box {
  width: 200px;
  margin: 100px auto;
  padding: 20px;
}

.wechat-logo {
  width: 48px;
  height: 48px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.wechat-logo:hover {
  transform: scale(1.1);
}

.wechat-logo:active {
  transform: scale(0.95);
}
</style>
