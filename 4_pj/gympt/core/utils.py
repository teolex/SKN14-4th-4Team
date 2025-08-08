from __future__ import annotations
from typing import List, Tuple

from langchain_openai import ChatOpenAI

import ast
import openai


# ------------------------------------------------------------------
# 유틸리티 함수들
# ------------------------------------------------------------------
def parse_prediction(pred_str: str) -> Tuple[str, str]:
    if isinstance(pred_str, dict):
        menu_name = next(iter(pred_str.values()))  # 첫 value
        return str(menu_name).strip(), ""
    try:
        menu_name, ingredients = ast.literal_eval(pred_str)[0]
        return menu_name.strip(), ingredients.strip()
    except Exception:
        # 파싱 실패 시 그대로 반환
        return pred_str.strip(), ""
    

# ------------------------------------------------------------------
# Pinecone 검색, Pinecone 결과 → 컨텍스트 형식 변환
# ------------------------------------------------------------------
def search_menu(vector_store, menu_name: str, k: int = 3):
    return vector_store.similarity_search_with_score(query=menu_name, k=k)


def build_context(matches) -> str:
    lines: List[str] = []
    for doc, score in matches:
        meta = doc.metadata or {}
        name = meta.get("RCP_NM", "알 수 없는 메뉴")
        kcal = meta.get("INFO_ENG", "칼로리 정보 없음")
        lines.append(f"- 메뉴명: {name}, 칼로리: {kcal} (유사도: {score:.2f})")
    return "\n".join(lines)

def ask_llm_calorie(menu_name: str) -> str:
    prompt = (
        "다음 음식의 대표적인 1인분 칼로리(kcal) 숫자만 알려주세요 "
        "**반드시 숫자만 반환!!**: '{menu}'"
    ).format(menu=menu_name)
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "250"


# ------------------------------------------------------------------
# 메뉴명 기반 컨텍스트 생성 + 칼로리 반환 개선 버전
# ------------------------------------------------------------------
def get_menu_context_with_threshold(
    vector_store,
    menu_name: str,
    k: int = 1,
    threshold: float = 0.4
):
    matches = search_menu(vector_store, menu_name, k)

    # 검색 결과가 없거나 유사도가 낮으면 LLM
    if not matches or matches[0][1] < threshold:
        calorie = ask_llm_calorie(menu_name)
        return f"- 메뉴명: {menu_name}, 칼로리: {calorie}", calorie

    # 문서 기반 정보 사용
    context = build_context(matches)
    doc, _ = matches[0]
    calorie = doc.metadata.get("INFO_ENG")

    # 칼로리 정보가 누락되어 있을 경우 fallback
    if not calorie or not str(calorie).isdigit():
        calorie = ask_llm_calorie(menu_name)

    return context, calorie


# ------------------------------------------------------------------
# 5. 최종 식단·운동 분석 프롬프트 작성 & 호출
# ------------------------------------------------------------------
def analyze_meal_with_llm(
    menu_infos: List[dict],
    user_info: dict,
    chat_history: list | None = None,
) -> str:
    """메뉴 리스트 + 사용자 정보 → GPT-4o 답변"""
    prompt_tmpl = """
[오늘 섭취한 음식 정보]
{foods_context}
{table}
총 섭취 칼로리: {total_calorie}kcal

아래는 지금까지의 대화 내역입니다.
{history_prompt}

사용자 정보: {user_info}


[답변 지침]
0. 대화의 첫 메시지에 ‘먹은 음식’이 명확히 포함돼 있거나 이미지가 전송이 되면 곧바로 1~8단계를 실행한다.  
    • 추가 확인 프롬프트(“어떤 음식을 드셨는지…”)를 띄우지 않는다.
1. 먹은 음식 각각의 칼로리 정보를 표로 보여준다.
2. 같은 음식명을 리스트로 한 번 더 요약한다.
3. 사용자의 신체 정보와 운동량을 고려하여 먹은 음식 총칼로리, 1일 권장 섭취량(2,000 kcal), 남은 칼로리를 계산한다.
4. 사용자가 섭취한 음식 총칼로리를 소모할 수 있도록
    • 근력운동 1가지
    • 유산소 1가지
    • 생활체육 1가지
    를 추천하며, 사용자가 추가적으로 운동 방향을 제시하면 그 방향에 맞춰 추천해줄 것. 소모열량 합계 = 먹은 음식 총칼로리(kcal) 로 맞춘다.
5. "이 열량을 소비하려면?" 섹션
    • 아래 예시처럼 **지구 n바퀴**, **에베레스트 n회 등반**, **올림픽 수영장 n바퀴**, **잠실 야구장 n바퀴**, **한강대교~마포대교 n회 왕복** 등
    • 일상‧스포츠‧지리적 비교를 **1줄**로 현실감있는 내용으로 유머 있게 표현한다.
    • 예시:
     - 지구 12바퀴 걷기와 비슷해요!
     - 에베레스트를 0.3번 오르는 정도예요!
     - 올림픽 수영장을 45바퀴 헤엄치는 격이죠!
     - 잠실 야구장을 8바퀴 도는 거리예요!
     - 한강대교부터 마포대교까지 6회 왕복하는 정도랍니다!
    • 매번 **다른 비교**를 무작위로 한가지 골라 사용해, 같은 예시가 반복되지 않도록 한다.
6. 남은 칼로리에 맞는 식단(아침·점심·저녁) 또는 간단한 간식을 추천한다.
7. 마지막에 "오늘의 한마디"로 응원하는 한 줄 멘트를 추가한다.
8. 모든 답변은 한국어로, 보기 좋게 **굵은 제목**, 표, 리스트를 활용한다.

[예외사항]
A. 사용자의 채팅에 음식이나 식단과 관련없는 내용만 있을 때
   1. 위 지침 A의 1~8 단계를 수행하지 않는다.
   2. 대신 한 문장으로 “어떤 음식을 드셨는지 알려 주세요! 음식명이나 사진을 보내 주세요.”라고 정중히 재요청한다.
   3. 반드시 다른 정보(표·운동·식단 등)는 출력하지 않는다.
"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

    history_prompt = ""
    if chat_history:
        for role, content, *_ in chat_history[-5:]:
            who = "사용자" if role == "user" else "GYM-PT"
            history_prompt += f"{who}: {content}\n"

    table_head = "| No | 파일명 | 음식명 | 칼로리 |\n|---|---|---|---|\n"
    table_body, foods_ctx, total_kcal = "", "", 0
    for i, info in enumerate(menu_infos, start=1):
        menu = info.get("menu_name", "")
        kcal = info.get("calorie", "")
        fname = info.get("filename", "")
        table_body += f"| {i} | {fname} | {menu} | {kcal} |\n"
        foods_ctx += f"{i}. {fname}: {menu} ({kcal}kcal)\n"
        try:
            total_kcal += int(float(kcal))
        except ValueError:
            pass

    prompt = prompt_tmpl.format(
        foods_context=foods_ctx,
        table=table_head + table_body,
        total_calorie=total_kcal,
        history_prompt=history_prompt,
        user_info=user_info,
    )
    return llm.invoke(prompt).content
