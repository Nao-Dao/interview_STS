- [ ] 语音VAD检测
```py
import ffmpeg
import io

def convert_webm_to_wav_binary(webm_data):
    try:
        # 使用 ffmpeg 通过管道处理 WebM 二进制数据并转换为 WAV
        # 创建一个 BytesIO 流来接收输出的 WAV 数据
        wav_output = io.BytesIO()

        # 调用 ffmpeg，输入 webm 数据，通过管道输出 WAV 格式的二进制数据
        process = (
            ffmpeg
            .input('pipe:0')  # 通过管道输入
            .output('pipe:1', format='wav')  # 通过管道输出为 WAV 格式
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )

        # 将 WebM 二进制数据写入到 ffmpeg 的 stdin
        stdout_data, stderr_data = process.communicate(input=webm_data)

        # 如果没有错误，stdout_data 即为转换后的 WAV 数据
        if process.returncode == 0:
            wav_output.write(stdout_data)
            wav_output.seek(0)  # 移动文件指针到开始位置

            # 返回转换后的 WAV 数据
            return wav_output.read()

        else:
            raise Exception(f"ffmpeg 错误: {stderr_data.decode('utf-8')}")
        
    except Exception as e:
        print(f"转换失败: {e}")
        return None

# 示例使用：将 WebM 二进制数据转换为 WAV 二进制数据
with open('input.webm', 'rb') as f:
    webm_data = f.read()  # 读取 WebM 文件为二进制数据

wav_data = convert_webm_to_wav_binary(webm_data)

if wav_data:
    with open('output.wav', 'wb') as f:
        f.write(wav_data)  # 将转换后的 WAV 二进制数据写入文件
    print("成功转换并保存为 WAV 文件")
```


- [ ] 流式语音输入

