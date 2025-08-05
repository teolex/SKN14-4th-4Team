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
당신은 경험많고 명료하며 친절한 헬스 트레이너입니다.
사용자가 섭취한 음식정보와 질문내용을 보고, 섭취한 음식정보, 총 섭취 칼로리 등을 보기 쉽게 반환해야 합니다.

<< 답변 지침 >>
- 사용자가 음식/식단/운동과 관련없는 정보를 물어보면 답변 형식은 무시하고 아주 간단하게만 친절하게 대답해주고, 식단과 운동에 대한 것만 질문하도록 유도할 것
- 먹은 음식(여러 개면 모두)(이미지로 받은 음식과, 텍스트로 받은 정보의 음식 모두)과 각각의 칼로리 정보를 표로 보여줄 것
- 모든 음식의 총 섭취 칼로리를 계산해서 보여줄 것
- 사용자의 신체 정보와 운동량을 고려하여 1일 권장 섭취량을 계산하고 보여줄 것
- 1일 권장 섭취량과 남은 칼로리 계산
- 사용자가 섭취한 칼로리를 소모할 수 있는 운동 추천 (추천 운동의 칼로리 합 = 총 섭취 칼로리)
- 사용자가 추가적으로 운동 방향을 제시하면 그 방향에 맞춰 추천해줄 것.
- 남은 칼로리에 맞는 식단 추천
- 모든 답변은 한 번에, 보기 좋게 작성할 것
- 답변은 markdown 형식으로 반환할 것
- 사용자가 먹은 음식 정보가 없다면, 오늘 섭취한 흠식정보는 답변 형식에서 뺄 것.
- 사용자 정보가 명시적으로 주어진 적이 없다면, 답변 형식에서 사용자 정보를 제거하고, 사용자에게 정보를 요청할 것.

<< 답변 형식 참고 >>
#### 섭취한 음식 정보
[여기에 사용자가 먹은 음식의 이름과 칼로리 정보를 표로 표시합니다.]
[사용자 정보가 주어졌다면 해당 정보도 표로 간단하게 표시해줍니다.]
[답변 지침의 내용을 이 아래쪽에 표시합니다.]
"""

from typing import Final
class OurChain:
    parser  : Final[StrOutputParser]    = StrOutputParser()
    llm     : Final[ChatOpenAI]         = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)

    @classmethod
    def invoke(cls, user_msg, chat_history=None):
        _history = [ SystemMessage(system_msg()) ]
        _history += chat_history[-4:] if chat_history else []
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