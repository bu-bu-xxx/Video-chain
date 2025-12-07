我想实现一个workflow：
用户输入图片和文字描述需求，根据用户需求生成每个视频片段的文字prompt，通过sora2 api输入文字prompt，并且输入上一个视频的最后帧画面作为图片prompt输入，进行每个视频片段的生成，以确保视频的coherent，最后拼接成一个长视频输出

development requriement:
1. 我们会使用`aihubmix`提供的sora2模型和gemini-3-pro-preview模型的api实现workflow
   
2. 所有提示词用中文
   
3. `aihubmix` `sora2` 模型调用方式Example：

Generate With a Reference Image:
```python
import requests

url = "https://aihubmix.com/v1/videos"

headers = {
    "Authorization": "Bearer sk-***"
}


# Prepare the multipart/form-data payload
files = {
    "prompt": (None, "The kitten is taking a nap under the tree."),
    "model": (None, "sora-2-pro"),
    "size": (None, "1280x720"),
    "seconds": (None, "4"),

    "input_reference": (
        "cat.jpeg",
        open("cat.jpeg", "rb"),
        "image/jpeg"
    )
}

response = requests.post(url, headers=headers, files=files)

print("Status:", response.status_code)
print("Response:", response.text)
```

Generate Without a Reference Image:
```python
import requests
import json

url = "https://aihubmix.com/v1/videos"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-***"
}

payload = {
    "model": "sora-2",
    "prompt": "A astronaut floating in space, holding a glowing plant, with Earth and stars in the background, slow-motion movement",
    "size": "720x1280",
    "seconds": '4',
}

response = requests.post(url, headers=headers, json=payload)

print("Status Code:", response.status_code)
print("Response:", response.text)
```


4. `aihubmix` `gemini-3-pro-preview` 模型调用方式Example：
```python
from openai import OpenAI

client = OpenAI(
    api_key="AIHUBMIX_API_KEY", # Your Key "sk-***"
    base_url="https://aihubmix.com/v1"
)

response = client.responses.create(
    model="gemini-3-pro-preview", 
    input=[
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": "what is in this image?" },
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                }
            ]
        }
    ]
)

print(response)
```

4. 先开发一个command line方式运行这个workflow，然后开发一个web界面可以运行以及展示
