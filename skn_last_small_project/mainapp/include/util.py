import ast
from typing import List, Tuple

import openai
from langchain_openai import ChatOpenAI


# 유틸리티 함수들
def parse_prediction(pred_str: str) -> Tuple[str, str]:
    """모델이 반환한 결과에서 음식 사진의 이름과 재료를 튜플로 파씽하여 반환"""
    try:
        parsed = ast.literal_eval(pred_str)
        menu_name, ingredients = parsed[0]
        return menu_name.strip(), ingredients.strip()
    except:
        return pred_str, ""

# --- 3. Pinecone 검색 ---
def search_menu(vector_store, menu_name: str, k: int = 3) -> List[Tuple]:
    return vector_store.similarity_search_with_score(query=menu_name, k=k)


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
def get_menu_context_with_threshold(
        vector_store,
        menu_name: str,
        k: int = 1,
        threshold: float = 0.4
) -> Tuple[str, str]:

    matches = search_menu(vector_store, menu_name, k)


    if not matches or matches[0][1] < threshold:
        # 유사도 낮을 경우 LLM으로 fallback
        calorie = ask_llm_calorie(menu_name)
        context = f"- 메뉴명: {menu_name}, 칼로리: {calorie}"
        return context, calorie

    # 유사한 문서가 충분함 → 문서에서 kcal 추출
    context = build_context(matches)
    # 가장 첫 번째 문서 정보 사용
    doc, _ = matches[0]
    calorie = doc.metadata.get("INFO_ENG")

    # 칼로리 정보가 누락되어 있을 경우 fallback
    if not calorie or not str(calorie).isdigit():
        calorie = ask_llm_calorie(menu_name)

    # print("음식 정보 컨텍스트", "-"*40, context, sep="\n", end="\n")

    return context, calorie


def analyze_meal_with_llm(menu_infos, user_info, rag_context="", chat_history=None) -> str:
    prompt_tmpl = """
[오늘 섭취한 음식 정보]
{foods_context}
{table}
총 섭취 칼로리: {total_calorie}kcal

아래는 지금까지의 대화 내역입니다.
{history_prompt}

사용자 정보: {user_info}

[답변 지침]
- 먹은 음식(여러 개면 모두)(이미지로 받은 음식과, 텍스트로 받은 정보의 음식 모두)과 각각의 칼로리 정보를 표로 보여줄 것
- 모든 음식의 총 섭취 칼로리를 계산해서 보여줄 것
- 사용자의 신체 정보와 운동량을 고려하여 1일 권장 섭취량을 계산하고 보여줄 것
- 1일 권장 섭취량과 남은 칼로리 계산
- 사용자가 섭취한 칼로리를 소모할 수 있는 운동 추천 (추천 운동의 칼로리 합 = 총 섭취 칼로리)
- 사용자가 추가적으로 운동 방향을 제시하면 그 방향에 맞춰 추천해줄 것.
- 남은 칼로리에 맞는 식단 추천
- 모든 답변은 한 번에, 보기 좋게 작성할 것
"""
    try:
        llm = ChatOpenAI(model='gpt-4o-mini', temperature=0.3)
        history_prompt = ""
        if chat_history:
            for i, (role, content, images) in enumerate(chat_history[-5:]):
                who = "사용자" if role == "user" else "GYM-PT"
                history_prompt += f"{who}: {content}\n"

        # 여러 음식 정보 표와 요약 만들기
        table = "| No | 파일명 | 음식명 | 칼로리 |\n|---|---|---|---|\n"
        foods_context = ""
        total_calorie = 0
        for i, info in enumerate(menu_infos):
            menu = info.get("menu_name", "")
            kcal = info.get("calorie", "")
            filename = info.get("filename", "")
            table += f"| {i + 1} | {filename} | {menu} | {kcal} |\n"
            foods_context += f"{i + 1}. {filename}: {menu} ({kcal}kcal)\n"
            try:
                total_calorie += int(float(kcal))
            except:
                pass

        prompt = prompt_tmpl.format(foods_context=foods_context, table=table, total_calorie=total_calorie, history_prompt=history_prompt, user_info=user_info)
        result = llm.invoke(prompt)

        # print("최종 결과 답변", "-"*40, result.content, sep="\n", end="\n")

        return result.content
    except Exception as e:
        return f"분석 중 오류가 발생했습니다: {str(e)}"