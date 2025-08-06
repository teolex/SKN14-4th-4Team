# # analyzer/views.py

# import json
# from django.http import JsonResponse
# from django.shortcuts import render
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# from PIL import Image

# # 위에서 만든 services.py 파일의 함수와 클래스를 임포트합니다.
# from .apps import (
#     OpenAIInferer,
#     parse_prediction,
#     get_menu_context_with_threshold,
#     analyze_meal_with_llm,
#     ask_llm_calorie,
# )

# # OpenAIInferer 인스턴스 생성
# inferer = OpenAIInferer()

# @csrf_exempt # API 테스트를 위해 CSRF 보호를 임시로 비활성화합니다.
# @require_http_methods(["POST"]) # 이 뷰는 POST 요청만 허용합니다.
# def analyze_view(request):
#     try:
#         # Flask의 request.content_type과 유사
#         content_type = request.content_type
#         user_text = ""
#         images = []
        
#         # JSON 요청 처리
#         if 'application/json' in content_type:
#             data = json.loads(request.body)
#             user_text = data.get("user_text", "")
#         # Form 데이터(이미지 포함) 처리
#         else:
#             images = request.FILES.getlist("images")
#             user_text = request.POST.get("user_text", "")

#         menu_infos = []

#         # 1. 이미지 처리
#         if images:
#             pil_images = [Image.open(img).convert("RGB") for img in images]
#             filenames = [img.name for img in images]
            
#             # OpenAIInferer를 호출하여 음식 이름과 재료 예측
#             predictions = inferer(pil_images, filenames)
            
#             for filename, pred_str in predictions.items():
#                 menu_name, ingredients = parse_prediction(pred_str)
#                 rag_context, calorie = get_menu_context_with_threshold(menu_name)
#                 menu_infos.append({
#                     "filename": filename,
#                     "menu_name": menu_name,
#                     "calorie": calorie,
#                     "ingredients": ingredients,
#                     "rag_context": rag_context,
#                 })
#         # 2. 텍스트만 있는 경우 처리
#         elif user_text:
#             # 텍스트로 받은 음식 이름의 칼로리 정보 가져오기
#             rag_context, calorie = get_menu_context_with_threshold(user_text)
#             menu_infos.append({
#                 "filename": "-",
#                 "menu_name": user_text,
#                 "calorie": calorie,
#                 "ingredients": "", # 텍스트 입력에는 재료 정보가 없음
#                 "rag_context": rag_context
#             })
            
#         # 3. LLM을 통한 최종 식단 분석
#         # user_info에는 사용자의 추가 정보를 전달할 수 있습니다 (예: 성별, 나이, 목표 등).
#         # 여기서는 편의상 user_text를 사용합니다.
#         result = analyze_meal_with_llm(
#             menu_infos=menu_infos,
#             user_info=user_text, # 필요에 따라 사용자의 상세 정보로 대체
#             chat_history=[] # 채팅 기록이 있다면 이곳에 전달
#         )

#         return JsonResponse({"content": result})

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)


# # 채팅 UI를 렌더링하는 뷰
# def chat_ui_view(request):
#     return render(request, 'app/chatbot.html')

# import os
# from langchain_openai import ChatOpenAI
# # 간단한 챗봇 API 뷰
# @csrf_exempt
# @require_http_methods(["POST"])
# def chat_api_view(request):
#     try:
#         data = json.loads(request.body)
#         user_msg = data.get("message", "")
        
#         # 간단한 LLM 호출 (Flask 코드와 동일)
#         # 실제 앱에서는 여기에 더 복잡한 대화 관리 로직이 필요합니다.
#         llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
#         response = llm.invoke(user_msg)
        
#         return JsonResponse({"response": response.content})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)




from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, HttpResponse
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
import uuid
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Create your views here.

load_dotenv()
model = ChatOpenAI(model_name='gpt-4.1', temperature=0.3)

prompt = ChatPromptTemplate.from_messages([
('system', '''
    너는 IT분야 최고의 직업상담사 챗봇이다. 진로를 고민하는 취업준비생에게 현실적이면서, 용기를 줄 수 있는 말투로 상담을 진행해야한다.
'''),
MessagesPlaceholder(variable_name='history'),
('human', '{query}')
])
chain = prompt | model

# in-memory에서 여러 개의 채팅내역을 보관하는 dict
# - key: sessionId
# - value: InMemoryChatMessageHistory 
store = {}

def get_by_session_id(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_by_session_id,
    input_messages_key='query',
    history_messages_key='history'
)

def invoke(query, session_id):
    return chain_with_history.invoke(
    {'query':query},
    config={
        'configurable':{
        'session_id': session_id
        }
    }
)

def index(request):
    return render(request, 'app/index.html')


# 비동기요청으로 처리될 3개의 뷰
def init_chat(request):
    """
    채팅별 고유한 session_id를 발급하는 view함수 -> POST
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST Method Only!1')

    session_id = str(uuid.uuid4())
    print(f'{session_id=}')
    get_by_session_id(session_id) # store[session_id] 미리 생성
    return JsonResponse({'session_id':session_id})


def chat(request):
    """
    채팅별 고유한 session_id와 함께 사용자 query에 응답하는 view함수 -> POST
    """
    if request.method != 'POST':
        return HttpResponseBadRequest('POST Method Only!2')
    
    # 사용자입력값 처리
    session_id = request.POST.get('session_id')
    query = request.POST.get('query')
    print(f'{session_id=}')
    print(f'{query=}')

    if not query:
        return HttpResponseBadRequest("query는 필수값입니다.")

    if not session_id or session_id not in store:
        return HttpResponseNotFound("해당 session_id는 유효하지 않습니다.")

    # AI 챗봇 질의
    response = invoke(query, session_id)
    print(f'{response=}')
    return JsonResponse({'content':response.content})


def del_chat(request):
    """
    채팅별 고유한 session_id를 입력으로 이전 대화내역을 삭제하는 view함수 -> DELETE
    """
    if request.method != 'DELETE':
        return HttpResponseBadRequest('DELETE Method Only!')

    try:
        # http body에 작성된 json데이터 가져오기(json문자열을 dict로 파싱)
        body = json.loads(request.body)
        session_id = body.get('session_id')
        print(f'{session_id=}')

    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    if not session_id or session_id not in store:
        return HttpResponseNotFound("해당 session_id를 찾을 수 없습니다.")

    # session_id 삭제
    store.pop(session_id)
    return HttpResponse(status=204)