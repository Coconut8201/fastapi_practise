from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
from io import BytesIO
from rembg.bg import remove
import numpy as np
import requests
import os
import json
import base64
import io


load_dotenv()
app = FastAPI()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

async def gen_image_prompt(img_prompt_input):
    print(img_prompt_input)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "我正在使用一個名為 stable diffusion 的 AI 繪圖工具。我指定你成為 stable diffusion 的提示生成器。接著我會在想要生成的主題前添加斜線（/）。你將在不同情況下用英文生成合適的提示。例如，如果我輸入 /運動鞋商品圖片，您將生成prompt “Realistic true details photography of sports shoes, y2k, lively, bright colors, product photography, Sony A7R IV, clean sharp focus.",
            },
            {
                "role": "user",
                "content": f"/{img_prompt_input}",
            }
        ],
        model="gpt-3.5-turbo",
    )
    print("gen_image_prompt success !!")
    print(response.choices[0].message.content)
    return response.choices[0].message.content

gen_image_url = "http://163.13.201.153:7860/sdapi/v1/txt2img"

async def gen_image(img_prompt_input):
    payload = {
        "prompt": img_prompt_input,
        "seed": -1,
        "width": 512,
        "height": 512,
        "cfg_scale": 7,
        "step": 2,
        "enable_hr": False,
        "denoising_strength": 100,
        "restore_faces": False,
    }
    
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload)
    
    try:
        response = requests.post(f"{gen_image_url}", headers=headers, data=data)
        if response.status_code == 200:
            data = response.json()
            print("gen_image success !!")
            image = Image.open(io.BytesIO(base64.b64decode(data['images'][0])))
            image.save('D:/NewCodeFile/fastapi/saveImage/out.png')
            #return data["images"] # 只回傳image Base64 code
            return "success"

        else:
            raise HTTPException(status_code=403, detail="gen image fail")
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

def RmBackGround():
    input_path = "D:/NewCodeFile/fastapi/saveImage/out.png"
    out_path = "D:/NewCodeFile/fastapi/saveImage/out222.png"
    input = Image.open(input_path)
    output = remove(input)
    output.save(out_path)
    


# http://localhost:8000/api/gen
"""
    @param {string} imgPromptInput - 使用者傳遞的圖片 prompt
"""
@app.post("/api/gen")
async def gen_image_endpoint(request: Request):
    img_prompt_input = request.query_params.get("imgPromptInput")
    image_prompt = await gen_image_prompt(img_prompt_input)
        
    if image_prompt is None:
        raise HTTPException(status_code=403, detail="gen image error")

    print("gen_image success")
    result = await gen_image(image_prompt)
    RmBackGround()
    return {"message": result}
