<script setup lang="ts">
import { useRouter } from "vue-router";
import { ElButton } from "element-plus";
import wechatLogo from "@/assets/images/wechat.png";
import { useUserInfo } from "../store/UserInfo";

const router = useRouter();
const user = useUserInfo();

const handleLogin = async () => {
  try {
    await user.login();
  } catch (error) {
    console.error("WeChat login failed:", error);
  }
};

</script>

<template>
  <div style="text-align: center">
    <div v-if="!user.isAuthenticated">
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
        <h2>你好, {{ user.userInfo?.nickname }}. 请点击开始采访</h2>
        <el-button class="form-button" @click="router.push(`/auto`)"
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
