<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useSystemConfig } from '../store/Config';
import { AudioPlayer } from '../util/audio/AudioPlayer';
import { StreamAudioRecord } from '../util/audio/AudioRecord';
import { VisualAudio } from '../util/audio/VisualAudio';
import { useRoute, useRouter } from 'vue-router';

const router = useRouter();
const route = useRoute();
const cid = route.params.cid as string;
const config = useSystemConfig();

const ws = new WebSocket(config.getWS("/ws"));
ws.addEventListener("open", () => {
    ws.send(JSON.stringify({
        action: "init",
        param: {
            sampleRate: ar.sampleRate,
            cid: cid
        }
    }));
});
ws.addEventListener("message", (e) => {
    if (e.data == "tts:start") {
        ap.stop();
        ap.load(config.getURL(`/api/tts/stream?cid=${cid}`));
        ap.start();
    } else if (e.data == "tts:stop") {
        ap.stop();
    }
});
ws.addEventListener("close", () => {
    // 链接的话，就返回首页
    router.push("/");
    location.reload();
});

const ap = new AudioPlayer();

const ar = new StreamAudioRecord();
ar.addEventListener("record", async (blob) => {
    const fileReader = new FileReader();
    fileReader.addEventListener("loadend", () => {
        const base64Audio = (fileReader.result as string).split(",")[1];
        ws.send(JSON.stringify({
            action: "record",
            param: {
                audio: base64Audio
            }
        }));
    });
    fileReader.readAsDataURL(blob);
});
ar.addEventListener("stop", () => {
    ws.send(JSON.stringify({
        action: "finish"
    }));
});

onMounted(() => {
    new VisualAudio({
        width: 400,
        height: 400
    }).start("#visualizer", ar, ap);
});


/**
 * 下面是激活聊天, 避免错误
 */
const record = ref(false);
const click = () => { record.value = !record.value; }
watch(record, (n) => {
    if (n) {
        ar.start();
    } else {
        ar.stop();
    }
});
</script>

<template>
    <div class="test-box">
        <div class="visualizer-container" @click="click">
            <canvas id="visualizer"></canvas>
        </div>
        <div class="tip" @click="click">
            {{ !record ? "开始聊天" : "结束聊天" }}
        </div>
    </div>
</template>

<style scoped>
.test-box {
    display: block;
    width: 100vw;
    height: 100vh;
    line-height: 0px;
}

.visualizer-container {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    cursor: pointer;
}

.tip {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    cursor: pointer;
}
</style>