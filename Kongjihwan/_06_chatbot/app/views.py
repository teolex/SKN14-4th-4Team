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