<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useSystemConfig } from '../store/Config';
import { ElButton } from 'element-plus';

const config = useSystemConfig();

const cid = ref<number>(-1);
fetch(config.getURL("/api/id"))
    .then(r => r.text())
    .then(r => {
        cid.value = parseInt(r);
    });

const router = useRouter();
</script>

<template>
    <div style="text-align: center;">
        <div>{{ cid }}</div>
        <template v-if="cid > 0">
            <el-card class="login-box">
                <el-button class="form-button" @click="router.push(`/manual/${cid}`);">manual</el-button>
                <el-button class="form-button" @click="router.push(`/auto/${cid}`);">auto</el-button>
            </el-card>
        </template>
    </div>
</template>

<style lang="css" scoped>

</style>