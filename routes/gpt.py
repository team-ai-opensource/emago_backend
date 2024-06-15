from openai import OpenAI
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os


# .env 파일 로드
load_dotenv('.env')

api_key = os.getenv('OPENAI_API_KEY')


# API 키 등록 필요
client = OpenAI(api_key=api_key)

gpt_touter = APIRouter(tags=["GPT"])

# Firebase Admin SDK
cred = credentials.Certificate("emago-e8c29-firebase-adminsdk-vhw9g-d31d7e2fea.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


class Prompt(BaseModel):
    messageId: str
    message: str

@gpt_touter.post("/api/emago")
def post_emago(prompt: Prompt):
    prompt = dict(prompt)
    my_message = prompt["message"]

    completion = client.chat.completions.create(
    model="gpt-4o-2024-05-13",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": """
        너는 AI 영어 선생님이야.
        우리가 영어로 이야기를 나눈 채팅 메세지를 너에게 보내 줄 건데,
        그 영어 메세지를 보고, 니가 특정 JSON 형식에 맞게 피드백을 줬으면 좋겠어.

        대답형식 :
        { 
        "comment" : "영어선생님으로써 메세지에 대한 자세한 한국어 코멘트", 
        "advanced_sentence" : "같은 표현의 다른 고급문장", 
        "error_sentence" : "메세지에서 문법상 잘 못 된 부분", 
        "correct_sentence" : "메세지에서 잘 못 된 부분의 문법을 고친 문장" 
        }

        바로 코드에서 아웃풋 값을 사용가능하게 위의 JSON 형식대로 답변해줘.
        """},
        {"role": "user", "content": my_message}
    ]
    )

    message = completion.choices[0].message.content

    # JSON 문자열을 딕셔너리로 변환
    dict_message = json.loads(message)

    # Update Firestore document
    try:
        doc_ref = db.collection("Messages").document(prompt["messageId"])
        doc_ref.update({"feedback": dict_message})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firestore update error: {str(e)}")

    return {'message': "업데이트 성공"}
