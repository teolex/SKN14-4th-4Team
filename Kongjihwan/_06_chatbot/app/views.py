from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound, HttpResponse
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage
import uuid
import json
import base64
import ast
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
import os
from typing import List, Tuple, Dict, Any
from pinecone import Pinecone
# Create your views here.

load_dotenv()


# 기존 일반 채팅용 모델
model = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.3)

# 이미지 분석용 모델
vision_model = ChatOpenAI(model="gpt-4o", temperature=0.3)

# Pinecone 초기화
try:
    pinecone_api_key = os.getenv("PINECONE_PJ_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "food-database")
    # pc = Pinecone(api_key=os.getenv("PINECONE_PJ_KEY"))
    embeddings = OpenAIEmbeddings()
    vector_store = PineconeVectorStore(
        embedding=embeddings,
        pinecone_api_key=pinecone_api_key
    )
    print("✅ Pinecone 연결 성공!")
except Exception as e:
    print(f"❌ Pinecone 연결 실패: {e}")
    print(os.getenv("PINECONE_PJ_KEY"))
    vector_store = None

# 기존 일반 채팅 프롬프트
prompt = ChatPromptTemplate.from_messages([
  ('system', '''
당신은 건강한 식단과 운동을 도와주는 전문 트레이너 "GYM-PT" 입니다.
사용자의 질문에 친근하고 전문적으로 답변해주세요.

**중요: 모든 답변은 반드시 한국어로만 해주세요.**

- 음식, 칼로리, 운동, 건강에 관련된 질문에 전문적으로 답변
- 구체적이고 실용적인 조언 제공const response
- 친근하고 격려하는 톤으로 대화
- 답변 언어: 한국어만 사용
'''),
  MessagesPlaceholder(variable_name='history'),
  ('human', '{query}')
])
chain = prompt | model

# in-memory에서 여러 개의 채팅내역을 보관하는 dict
store = {}

@csrf_exempt
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

@csrf_exempt
def invoke_text_only(query, session_id):
  """텍스트만 있는 일반 채팅"""
  return chain_with_history.invoke(
    {'query': query},
    config={
      'configurable': {
        'session_id': session_id
      }
    }
  )

# ==================== 🍎 음식 분석 관련 함수들 ====================
@csrf_exempt
def extract_food_names_from_images(images: List[any]) -> List[str]:
    """이미지에서 음식명 추출"""
    image_contents = []
    
    for image in images:
        if hasattr(image, 'read'):
            # Django UploadedFile
            img_bytes = image.read()
            image.seek(0)  # 파일 포인터 리셋
        else:
            # bytes 데이터
            img_bytes = image
        
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })
    
    # 음식 인식 프롬프트
    prompt_text = '''
당신은 전 세계 음식들을 모두 다 알고 있는 음식전문가입니다.

당신은 사용자가 제시한 음식 이미지의 정확한 음식명을 반환해야 합니다.
- 답변은 반드시 단답형의 음식명과 그 음식에 들어간 재료 목록을 반환해야 합니다.
- 음식명과 재료목록은 ("음식명", "재료목록") 의 형태로 답변해야 합니다.
- 음식명과 재료목록은 반드시 한글이어야 합니다.
- 답변은 [("음식명", "재료목록")] 과 같이 배열로 감싼 형태여야 합니다.
- 이미지에 음식의 개수가 여러가지라면, 최대 5개의 음식을 배열로 감싸서 반환합니다.

< 답변 예시 >
[("짜장면", "춘장, 돼지고기, 양파, 면, 카라멜")]
[("햄버거", "패티, 번, 양상추, 양파, 머스타드소스, 치즈, 피클"), ("베이컨 연어 셀러드", "베이컨, 훈제연어, 양상추, 토마토")]
'''
    
    content = [{"type": "text", "text": prompt_text}]
    content.extend(image_contents)
    
    messages = [HumanMessage(content=content)]
    response = vision_model.invoke(messages)
    
    try:
        # 문자열을 파이썬 리스트로 변환
        food_list = ast.literal_eval(response.content)
        return food_list
    except:
        return [(response.content, "")]
@csrf_exempt
def search_menu_in_pinecone(menu_name: str, k: int = 3) -> List[Tuple]:
    """Pinecone에서 메뉴 검색"""
    if not vector_store:
        return []
    try:
        return vector_store.similarity_search_with_score(query=menu_name, k=k)
    except Exception as e:
        print(f"Pinecone 검색 오류: {e}")
        return []
@csrf_exempt
def ask_llm_calorie(menu_name: str) -> str:
    """LLM으로 칼로리 정보 요청"""
    try:
        prompt_msg = f"다음 음식의 대표적인 1인분 칼로리(kcal) 숫자만 알려주세요. 반드시 숫자만 반환: '{menu_name}'"
        response = vision_model.invoke([HumanMessage(content=prompt_msg)])
        # 숫자만 추출
        calorie = ''.join(filter(str.isdigit, response.content))
        return calorie if calorie else "250"
    except Exception as e:
        print(f"LLM 칼로리 요청 오류: {e}")
        return "250"
@csrf_exempt
def get_menu_context_with_threshold(menu_name: str, k: int = 3, threshold: float = 0.4) -> Tuple[str, str]:
    """Pinecone에서 음식 정보 검색 (임계값 적용)"""
    matches = search_menu_in_pinecone(menu_name, k)
    
    if not matches or matches[0][1] < threshold:
        # 유사도가 낮으면 LLM fallback
        calorie = ask_llm_calorie(menu_name)
        context = f"메뉴명: {menu_name}, 칼로리: {calorie}kcal (LLM 추정)"
        return context, calorie
    
    # 가장 유사한 문서에서 정보 추출
    doc, score = matches[0]
    menu_name_db = doc.metadata.get("RCP_NM", menu_name)
    calorie = doc.metadata.get("INFO_ENG", "")
    
    # 칼로리 정보 검증
    if not calorie or not str(calorie).replace('.', '').isdigit():
        calorie = ask_llm_calorie(menu_name)
    
    context = f"메뉴명: {menu_name_db}, 칼로리: {calorie}kcal (DB 검색, 유사도: {score:.2f})"
    return context, str(calorie)
@csrf_exempt
def analyze_meal_with_llm(menu_infos: List[Dict], user_text: str, session_id: str) -> str:
    """음식 분석 + 영양상담"""
    try:
        # 음식 정보 테이블 생성
        total_calorie = 0
        table = "| 번호 | 음식명 | 칼로리 | 재료 |\n|---|---|---|---|\n"
        foods_context = ""
        
        for i, info in enumerate(menu_infos, 1):
            menu_name = info.get("menu_name", "")
            ingredients = info.get("ingredients", "")
            calorie = info.get("calorie", "0")
            
            table += f"| {i} | {menu_name} | {calorie}kcal | {ingredients} |\n"
            foods_context += f"{i}. {menu_name} ({calorie}kcal) - 재료: {ingredients}\n"
            
            try:
                total_calorie += int(float(calorie))
            except:
                pass
        
        # 이전 대화 내역 가져오기
        chat_history = get_by_session_id(session_id)
        history_text = ""
        for msg in chat_history.messages[-6:]:  # 최근 6개 메시지만
            role = "사용자" if msg.type == "human" else "GYM-PT"
            history_text += f"{role}: {msg.content}\n"
        
        # 종합 분석 프롬프트
        analysis_prompt = f"""
당신은 건강한 식단과 운동을 도와주는 전문 트레이너 "GYM-PT" 입니다.

[이전 대화 내역]
{history_text}

[오늘 섭취한 음식 분석 결과]
{table}

상세 정보:
{foods_context}

총 섭취 칼로리: {total_calorie}kcal

사용자 추가 정보: {user_text}

다음 형식으로 친근하고 전문적으로 답변해주세요:

🍎 **음식 분석 결과**
- 섭취한 음식들과 각각의 칼로리 (표 형태로 정리)
- 총 섭취 칼로리: {total_calorie}kcal

📊 **개인별 권장사항**
- 사용자 정보 기반 일일 권장 섭취량 계산
- 남은 권장 섭취량 계산

🏃‍♂️ **운동 추천**
- 섭취한 칼로리를 소모할 수 있는 구체적인 운동 방법들
- 운동 시간과 칼로리 소모량 명시

🥗 **식단 조언**
- 남은 칼로리에 맞는 추천 식단
- 영양 균형 고려한 조언

💪 **격려의 말**
- 긍정적이고 동기부여가 되는 마무리

**다시 한 번 강조: 모든 답변은 한국어로만 작성해주세요!**

모든 답변은 친근하고 격려하는 톤으로, 구체적이고 실용적인 정보를 제공해주세요!
"""
        
        response = vision_model.invoke([HumanMessage(content=analysis_prompt)])
        return response.content
        
    except Exception as e:
        return f"""
🍎 **음식 분석 결과 (Demo)**

안녕하세요! GYM-PT입니다 😊

업로드해주신 음식들을 분석한 결과:
- 총 섭취 칼로리: 약 600kcal로 추정됩니다

📊 **권장사항:**
- 일일 권장 섭취량: 약 2,200kcal
- 남은 권장량: 약 1,600kcal

🏃‍♂️ **운동 추천:**
- 빠른 걷기 90분 (600kcal 소모)
- 자전거 타기 60분 (600kcal 소모)
- 조깝 45분 (600kcal 소모)

💪 건강한 식단 관리 화이팅입니다!

*API 연결 오류: {str(e)}*
"""
@csrf_exempt
def invoke_with_images(query, images, session_id):
    """이미지가 포함된 채팅 처리"""
    try:
        # 1. 이미지에서 음식명 추출
        food_predictions = extract_food_names_from_images(images)
        print(f"🍎 추출된 음식들: {food_predictions}")
        
        # 2. 각 음식에 대해 Pinecone 검색
        menu_infos = []
        for prediction in food_predictions:
            if isinstance(prediction, tuple):
                menu_name, ingredients = prediction
            else:
                menu_name, ingredients = str(prediction), ""
            
            # Pinecone에서 유사한 음식 검색
            context, calorie = get_menu_context_with_threshold(menu_name.strip())
            
            menu_infos.append({
                "menu_name": menu_name.strip(),
                "ingredients": ingredients.strip(),
                "calorie": calorie,
                "context": context
            })
            
            print(f"🔍 {menu_name}: {calorie}kcal")
        
        # 3. 종합 분석 수행
        analysis_result = analyze_meal_with_llm(menu_infos, query, session_id)
        
        # 4. 채팅 히스토리에 저장
        history = get_by_session_id(session_id)
        history.add_user_message(f"[이미지 {len(images)}개 업로드] {query}")
        history.add_ai_message(analysis_result)
        
        return type('Response', (), {'content': analysis_result})()
        
    except Exception as e:
        error_msg = f"이미지 분석 중 오류가 발생했습니다: {str(e)}"
        print(f"❌ 이미지 분석 오류: {e}")
        
        # 오류 시에도 히스토리에 저장
        history = get_by_session_id(session_id)
        history.add_user_message(f"[이미지 업로드 실패] {query}")
        history.add_ai_message(error_msg)
        
        return type('Response', (), {'content': error_msg})()

# ==================== 🌟 기존 뷰 함수들 ====================
@csrf_exempt
def index(request):
  return render(request, 'app/index.html')
@csrf_exempt
def init_chat(request):
  """채팅별 고유한 session_id를 발급하는 view함수 -> POST"""
  if request.method != 'POST':
    return HttpResponseBadRequest('POST Method Only!')
  
  session_id = str(uuid.uuid4())
  print(f'🆔 새로운 세션 생성: {session_id}')
  get_by_session_id(session_id) # store[session_id] 미리 생성
  return JsonResponse({'session_id': session_id})

@csrf_exempt
def chat(request):
  """🌟 이미지 분석이 통합된 채팅 view함수 -> POST"""
  if request.method != 'POST':
    return HttpResponseBadRequest('POST Method Only!')
  
  # 사용자입력값 처리
  session_id = request.POST.get('session_id')
  query = request.POST.get('query', '')
  images = request.FILES.getlist('images')  # 이미지 파일들
  
  print(f'💬 채팅 요청 - 세션: {session_id}')
  print(f'📝 텍스트: {query}')
  print(f'🖼️ 이미지 개수: {len(images)}')
  
  if not query and not images:
    return HttpResponseBadRequest("텍스트나 이미지 중 하나는 필요합니다.")
  
  if not session_id or session_id not in store:
    return HttpResponseNotFound("해당 session_id는 유효하지 않습니다.")
  
  try:
    # 🔥 핵심: 이미지가 있으면 음식 분석, 없으면 일반 채팅
    if images:
      print("🍎 이미지 분석 모드로 전환")
      # 최대 5개 이미지 제한
      if len(images) > 5:
        images = images[:5]
      response = invoke_with_images(query, images, session_id)
    else:
      print("💬 일반 채팅 모드")
      response = invoke_text_only(query, session_id)
    
    print(f'✅ AI 응답 완료')
    return JsonResponse({'content': response.content})
    
  except Exception as e:
    error_msg = f"처리 중 오류가 발생했습니다: {str(e)}"
    print(f'❌ 챗봇 오류: {e}')
    return JsonResponse({'content': error_msg})

@csrf_exempt
def del_chat(request):
  """채팅별 고유한 session_id를 입력으로 이전 대화내역을 삭제하는 view함수 -> DELETE"""
  if request.method != 'DELETE':
    return HttpResponseBadRequest('DELETE Method Only!')
  
  try:
    body = json.loads(request.body)
    session_id = body.get('session_id')
    print(f'🗑️ 채팅 삭제 요청: {session_id}')
  except Exception:
    return HttpResponseBadRequest("Invalid JSON")
  
  if not session_id or session_id not in store:
    return HttpResponseNotFound("해당 session_id를 찾을 수 없습니다.")
  
  # session_id 삭제
  store.pop(session_id)
  print(f'✅ 채팅 삭제 완료: {session_id}')
  return HttpResponse(status=204)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# def chatbot(request):
#     if request.method == 'POST':
#         user_text = request.POST.get('user_text')
#         images = request.FILES.getlist('image_0')  # JS 쪽에서 image_0, image_1... 이런 식으로 보내는 경우

#         # 🎯 여기에 OpenAI API 연동 및 음식 분석 로직 넣으면 됨
#         return JsonResponse({'result': f"받은 텍스트: {user_text}, 이미지 개수: {len(images)}"})
#     return JsonResponse({'error': 'Invalid request'}, status=400)


from django.http import JsonResponse
from PIL import Image
import os
import ast
from langchain_openai import ChatOpenAI
import base64
from langchain_core.messages import HumanMessage

@csrf_exempt
def analyze(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST 요청만 허용'}, status=400)

    user_text = request.POST.get('user_text', '')
    images = request.FILES.getlist('images')  # name="images"로 multiple 전송된 경우

    if not user_text and not images:
        return JsonResponse({'error': '텍스트나 이미지 중 하나는 필요합니다.'}, status=400)

    # LangChain 모델 세팅
    model = ChatOpenAI(model="gpt-4o", temperature=0.7)

    image_contents = []
    for image in images:
        img_bytes = image.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        image_contents.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{img_base64}"
            }
        })

    content = []
    if user_text:
        korean_instruction = "다음 질문에 대해 반드시 한국어로만 답변해주세요:\n\n" + user_text
        content.append({"type": "text", "text": korean_instruction})
    else:
        # 이미지만 있는 경우에도 한국어 응답 요청
        content.append({"type": "text", "text": "이미지를 분석하고 반드시 한국어로만 답변해주세요."})
        
    content.extend(image_contents)

    messages = [HumanMessage(content=content)]

    try:
        response = model.invoke(messages)
        return JsonResponse({'result': response.content})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)