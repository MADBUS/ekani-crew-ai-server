import re
from typing import Dict, Tuple

# 키워드 + 가이드라인 가중치 통합 사전
DICTIONARY = {
    "EI": {
        "E": [{"word": "같이", "w": 5}, {"word": "사람", "w": 3}, {"word": "모임", "w": 5}, {"word": "떠들", "w": 3},
              {"word": "만나", "w": 4}, {"word": "친구들", "w": 5}],
        "I": [{"word": "혼자", "w": 5}, {"word": "조용", "w": 4}, {"word": "집에", "w": 5}, {"word": "생각", "w": 3},
              {"word": "기빨려", "w": 5}, {"word": "이어폰", "w": 4}]
    },
    "SN": {
        "S": [{"word": "사실", "w": 5}, {"word": "현실", "w": 4}, {"word": "경험", "w": 4}, {"word": "직접", "w": 3},
              {"word": "구체적", "w": 5}, {"word": "팩트", "w": 3}],
        "N": [{"word": "의미", "w": 5}, {"word": "상상", "w": 5}, {"word": "미래", "w": 4}, {"word": "가능성", "w": 5},
              {"word": "만약에", "w": 5}, {"word": "비유", "w": 3}]
    },
    "TF": {
        "T": [{"word": "이유", "w": 5}, {"word": "원인", "w": 5}, {"word": "논리", "w": 5}, {"word": "분석", "w": 4},
              {"word": "왜", "w": 5}, {"word": "해결", "w": 4}, {"word": "보험", "w": 5}],
        "F": [{"word": "기분", "w": 5}, {"word": "마음", "w": 5}, {"word": "공감", "w": 5}, {"word": "서운", "w": 4},
              {"word": "감정", "w": 5}, {"word": "속상", "w": 5}, {"word": "어떡해", "w": 5}]
    },
    "JP": {
        "J": [{"word": "계획", "w": 5}, {"word": "정리", "w": 4}, {"word": "미리", "w": 5}, {"word": "확정", "w": 4},
              {"word": "리스트", "w": 5}, {"word": "예약", "w": 4}],
        "P": [{"word": "즉흥", "w": 5}, {"word": "그때", "w": 4}, {"word": "유연", "w": 4}, {"word": "대충", "w": 4},
              {"word": "일단", "w": 5}, {"word": "상황 봐서", "w": 4}]
    }
}

DESCRIPTIONS = {
    "ISTP": {"title": "만능 재주꾼", "traits": ["#냉철함", "#해결사"], "desc": "사고 현장에서도 수리비부터 계산할 쿨한 해결사군요!"},
    "ENFP": {"title": "재기발랄한 활동가", "traits": ["#에너지", "#인싸"], "desc": "세상을 즐거움으로 채우는 당신은 자유로운 영혼입니다!"},
    # (나머지 유형도 동일한 형식으로 추가 가능)
}


def calculate_partial_mbti(answers: list):
    scores = {k: 0 for k in "EISNTFJP"}
    
    # Process only the answers provided so far
    for i, ans in enumerate(answers):
        dim = ""
        if i < 3: dim = "EI"
        elif i < 6: dim = "SN"
        elif i < 9: dim = "TF"
        elif i < 12: dim = "JP"
        
        if not dim: # Should not happen if within 12 questions range
            continue

        # 1. 키워드 매칭
        for trait, keywords in DICTIONARY[dim].items():
            for k in keywords:
                # Ensure 'ans' is a string before checking 'in'
                if isinstance(ans, str) and k["word"] in ans:
                    scores[trait] += k["w"]

        # 2. 패턴 매칭 (정규표현식)
        if isinstance(ans, str): # Ensure 'ans' is a string before regex
            if dim == "SN" and re.search(r"만약에|~라면", ans): scores["N"] += 3
            if dim == "TF" and re.search(r"왜 그런지|이유가 뭐야", ans): scores["T"] += 4

    # 결과 계산 (부분적으로만 계산)
    partial_mbti = ""
    
    if answers and len(answers) > 0: # Only calculate if at least one question has been answered
        # EI
        if len(answers) >= 3:
            partial_mbti += ("E" if scores["E"] >= scores["I"] else "I")
        else:
            partial_mbti += "X" # Not enough questions yet

        # SN
        if len(answers) >= 6:
            partial_mbti += ("S" if scores["S"] >= scores["N"] else "N")
        else:
            partial_mbti += "X"

        # TF
        if len(answers) >= 9:
            partial_mbti += ("T" if scores["T"] >= scores["F"] else "F")
        else:
            partial_mbti += "X"

        # JP
        if len(answers) >= 12:
            partial_mbti += ("J" if scores["J"] >= scores["P"] else "P")
        else:
            partial_mbti += "X"
    else: # No answers given yet
        partial_mbti = "XXXX"
    
    return {"mbti": partial_mbti, "scores": scores}

def run_analysis(answers: list):
    scores = {k: 0 for k in "EISNTFJP"}

    for i, ans in enumerate(answers):
        dim = "EI" if i < 3 else "SN" if i < 6 else "TF" if i < 9 else "JP"

        # 1. 키워드 매칭
        for trait, keywords in DICTIONARY[dim].items():
            for k in keywords:
                if k["word"] in ans:
                    scores[trait] += k["w"]

        # 2. 패턴 매칭 (정규표현식)
        if dim == "SN" and re.search(r"만약에|~라면", ans): scores["N"] += 3
        if dim == "TF" and re.search(r"왜 그런지|이유가 뭐야", ans): scores["T"] += 4

    # 결과 계산
    res_mbti = (
            ("E" if scores["E"] >= scores["I"] else "I") +
            ("S" if scores["S"] >= scores["N"] else "N") +
            ("T" if scores["T"] >= scores["F"] else "F") +
            ("J" if scores["J"] >= scores["P"] else "P")
    )

    def get_conf(a, b):
        return round((abs(a - b) / (a + b + 0.1)) * 100, 1)

    confidence = {
        "EI": get_conf(scores["E"], scores["I"]),
        "SN": get_conf(scores["S"], scores["N"]),
        "TF": get_conf(scores["T"], scores["F"]),
        "JP": get_conf(scores["J"], scores["P"])
    }

    return res_mbti, scores, confidence


# 차원 양쪽 매핑
DIMENSION_SIDES: Dict[str, Tuple[str, str]] = {
    "EI": ("E", "I"),
    "SN": ("S", "N"),
    "TF": ("T", "F"),
    "JP": ("J", "P"),
}


def get_dimension_for_question(question_index: int) -> str:
    """
    질문 인덱스(0-based)에 해당하는 MBTI 차원을 반환합니다.

    Args:
        question_index: 0-based 질문 인덱스

    Returns:
        차원 문자열 ("EI", "SN", "TF", "JP")
    """
    if question_index < 3:
        return "EI"
    elif question_index < 6:
        return "SN"
    elif question_index < 9:
        return "TF"
    else:
        return "JP"


def analyze_single_answer(answer: str, dimension: str) -> Dict:
    """
    단일 답변에 대해 주어진 차원의 MBTI 점수를 분석합니다.

    Args:
        answer: 사용자 답변 텍스트
        dimension: MBTI 차원 ("EI", "SN", "TF", "JP")

    Returns:
        분석 결과 딕셔너리:
        {
            "content": 원본 답변,
            "dimension": 차원,
            "scores": {"E": 5, "I": 3},
            "side": 우세한 쪽,
            "score": 우세한 쪽 점수
        }
    """
    if dimension not in DIMENSION_SIDES:
        raise ValueError(f"Invalid dimension: {dimension}")

    side_a, side_b = DIMENSION_SIDES[dimension]
    scores = {side_a: 0, side_b: 0}

    # 1. 키워드 매칭
    for trait, keywords in DICTIONARY[dimension].items():
        for k in keywords:
            if k["word"] in answer:
                scores[trait] += k["w"]

    # 2. 패턴 매칭 (정규표현식)
    if dimension == "SN" and re.search(r"만약에|~라면", answer):
        scores["N"] += 3
    if dimension == "TF" and re.search(r"왜 그런지|이유가 뭐야", answer):
        scores["T"] += 4

    # 우세한 쪽 결정
    if scores[side_a] >= scores[side_b]:
        winning_side = side_a
        winning_score = scores[side_a]
    else:
        winning_side = side_b
        winning_score = scores[side_b]

    return {
        "content": answer,
        "dimension": dimension,
        "scores": scores,
        "side": winning_side,
        "score": winning_score,
    }