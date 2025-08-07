from typing import List, Tuple

import openai
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .vector_store import VStore


# --- 4. Pinecone 결과 → 컨텍스트 형식 변환 ---
def build_context(matches: List[Tuple]) -> str:
    lines = []
    for doc, score in matches:
        meta = doc.metadata or {}
        name = meta.get("RCP_NM", "알 수 없는 메뉴")
        kcal = meta.get("INFO_ENG", "칼로리 정보 없음")
        lines.append(f"- 메뉴명: {name}, 칼로리: {kcal} (유사도: {score:.2f})")
    return "\n".join(lines)


def ask_llm_calorie(menu_name: str) -> str:
    try:
        prompt = f"다음 음식의 대표적인 1인분 칼로리(kcal) 숫자만 알려주세요 **반드시 숫자만 반환!!**: '{menu_name}'"
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except:
        return "250"  # 기본값


# --- 6. 메뉴명 기반 컨텍스트 생성 + 칼로리 반환 개선 버전 ---
def get_menu_context_with_threshold(menu_name: str, k: int = 1, threshold: float = 0.4) -> Tuple[str, str]:
    vector_store = VStore.get_vec_store()                       # 벡터DB 에서 음식정보와 유사한 문서 검색
    matches = vector_store.similarity_search_with_score(query=menu_name, k=k)

    if not matches or matches[0][1] < threshold:                # 유사도 기준보다 낮으면
        calorie = ask_llm_calorie(menu_name)                    # LLM으로 fallback
        context = f"- 메뉴명: {menu_name}, 칼로리: {calorie}"
    else:                                                       # 유사한 문서가 충분하면
        context = build_context(matches)
        doc, _  = matches[0]                                    # 가장 첫 번째 문서 정보 사용
        calorie = doc.metadata.get("INFO_ENG")

        if not calorie or not str(calorie).isdigit():           # 칼로리 정보가 누락되어 있을 경우 fallback
            calorie = ask_llm_calorie(menu_name)

    return context, calorie

def system_msg() -> str:
    return """
당신은 섭취한 음식과 운동 정보를 분석해주는 식단/운동 전문AI, 💪 Gym-PT 입니다. 당신의 페르소나를 잊으면 안됩니다.
사용자가 입력한 텍스트를 참고하여 다음을 수행하세요:

- 사용자 질의가 사용자가 섭취한 음식/운동/식단과 관계가 있다면 사용자가 섭취한 음식의 이름, 각 음식의 열량(kcal), 총 섭취 열량, 총 열량을 소모하기 위한 추천운동을 표로 표시하세요.
  - 사용자가 먹은 음식의 정보 중에 날짜 정보가 있다면, 사용자가 따로 언급하지 않았더라도 그 날에 섭취한 음식을 모두 함께 계산해야 합니다.
  - 총 섭취열량은 각 음식의 열량을 표시한 표 안에 함께 표시되어야 합니다.
- 사용자가 신체 정보를 제공한 경우(`나이`, `성별`, `키(cm)`, `몸무게(kg)`가 포함되어 있다면), 해당 정보를 기반으로 적절한 운동 종목 3가지를 추천하고 표로 표시하세요.
- 사용자가 신체 정보를 제공하지 않았다면, 성인 평균을 참고하여 적절한 운동 종목 3가지를 추천하고 표로 표시하세요.
   동시에, 사용자에게 신체 정보가 있으면 좀 더 사용자에게 적합한 추천을 할 수 있다고 안내해주세요.  
- 만약 사용자의 질의가 음식이나 운동과 관련이 없는 경우, 아래 기준에 따라 답변을 다르게 해주세요.
  - 음식이나 운동과 관련없는 일상적인 질문일 경우, 질문의 의도에 맞는 답변을 전달해주세요. 이 때는 결과를 markdown 으로 주지 않아도 됩니다.
  - 음식 또는 운동과 관련은 없지만 식단/건강/수명 등에 대한 지식을 묻는 경우, 해당 지식에 대한 답변을 주세요.

운동과 칼로리 소모량 등의 수치를 표에서 보여줄 때는 반드시 <<표 출력 예시>> 들을 참고해야 합니다.
운동 종목을 추천할 때는 반드시 해당 운동의 분당 칼로리 소모량과 사용자가 섭취한 칼로리를 모두 소모하기 위해 소요되는 총 시간을 함께 표시해야 합니다.
결과는 반드시 Markdown 형식으로 반환하세요.  
식단과 운동 정보는 표(`|` 문법)로 나타내며, 제목은 `####` 수준으로 구분하세요.  
부가 설명은 최소화하고, 핵심 정보 위주로 간결하게 작성하세요.

<< 표 출력 예시1 >>
| 음식 | 열량 |
|---|---|
| 그릭 요거트 | 100 kcal |
| 햄버거 | 300 kcal |
| 총 합 | 400 kcal |

<< 표 출력 예시2 >>
| 운동 | 분당 칼로리 소모량 | 소요 시간 |
|---|---|---|
| 🏃 조깅 | 10 kcal/분 | 30 분 |
| 🚴 자전거 타기 | 8kcal/분 | 38분 | 
"""

from typing import Final
class OurChain:
    parser  : Final[StrOutputParser]    = StrOutputParser()
    llm     : Final[ChatOpenAI]         = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)

    @classmethod
    def invoke(cls, user_msg, chat_history=None):
        _history = [ SystemMessage(system_msg()) ]
        _history += chat_history[-10:] if chat_history else []
        _history += [ HumanMessage(user_msg) ]

        _prompt = ChatPromptTemplate.from_messages( _history )
        _chain  = _prompt | OurChain.llm | OurChain.parser

        result  = _chain.invoke({})

        return result

def analyze_meal_with_llm(context_info, chat_history=None):
    prompt_tmpl = """
[오늘 섭취한 음식 정보]
{foods_context}
총 섭취 칼로리: {total_calorie}kcal

사용자 입력 text: {text}
"""

    chat_history = [] if chat_history is None else chat_history

    if "user_info" in context_info:
        prompt_tmpl += f"\n\n사용자 정보 : {context_info['user_info']}"

    try:
        foods_context = []
        total_calorie = 0
        user_text     = context_info["user_text"]
        for i, info in enumerate(context_info["image_info"]):
            foods_context.append(info["rag_context"])
            try: total_calorie += int(info["calorie"])
            except: pass

        foods_context = "\n".join(foods_context)

        prompt = prompt_tmpl.format(foods_context=foods_context, total_calorie=total_calorie, text=user_text)
        result = OurChain.invoke(prompt, chat_history)

        chat_history += [
            ("human", user_text),
            ("ai"   , result)
        ]

        return result
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"