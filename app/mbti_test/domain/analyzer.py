import re

# ==========================================================
# 1. 데이터 영역 (키워드 사전)
# ==========================================================
DICTIONARY = {
    "EI": {
        "E": [
            {"word": "같이", "w": 5}, {"word": "사람", "w": 3}, {"word": "모임", "w": 5},
            {"word": "떠들", "w": 3}, {"word": "만나", "w": 4}, {"word": "친구들", "w": 5},
            {"word": "다같이", "w": 5}, {"word": "여럿이", "w": 5}, {"word": "파티", "w": 4},
            {"word": "술자리", "w": 4}, {"word": "회식", "w": 4}, {"word": "번개", "w": 5},
            {"word": "나가", "w": 3}, {"word": "밖에", "w": 3}, {"word": "외출", "w": 3},
            {"word": "약속", "w": 4}, {"word": "만남", "w": 4}, {"word": "대화", "w": 3},
            {"word": "수다", "w": 5}, {"word": "톡", "w": 3}, {"word": "전화", "w": 3},
            {"word": "연락", "w": 3}, {"word": "놀", "w": 4}, {"word": "함께", "w": 4},
            {"word": "우리", "w": 3}, {"word": "다들", "w": 3}, {"word": "활발", "w": 4},
            {"word": "시끌", "w": 4}, {"word": "왁자지껄", "w": 5}, {"word": "떠들썩", "w": 5}
        ],
        "I": [
            {"word": "혼자", "w": 5}, {"word": "조용", "w": 4}, {"word": "집에", "w": 5},
            {"word": "생각", "w": 3}, {"word": "기빨려", "w": 5}, {"word": "이어폰", "w": 4},
            {"word": "집콕", "w": 5}, {"word": "방콕", "w": 5}, {"word": "쉬고", "w": 3},
            {"word": "충전", "w": 4}, {"word": "휴식", "w": 3}, {"word": "피곤", "w": 4},
            {"word": "귀찮", "w": 4}, {"word": "나만", "w": 4}, {"word": "혼자만", "w": 5},
            {"word": "고요", "w": 4}, {"word": "조용히", "w": 4}, {"word": "차분", "w": 4},
            {"word": "은둔", "w": 5}, {"word": "방구석", "w": 5}, {"word": "침대", "w": 3},
            {"word": "집순이", "w": 5}, {"word": "집돌이", "w": 5}, {"word": "인싸 아닌", "w": 5},
            {"word": "조용한", "w": 4}, {"word": "깊이", "w": 3}, {"word": "내면", "w": 4},
            {"word": "사색", "w": 4}, {"word": "명상", "w": 4}, {"word": "독서", "w": 3},
            {"word": "힘들", "w": 4}, {"word": "힘듦", "w": 4}, {"word": "힘드노", "w": 4},
            {"word": "침묵", "w": 5}, {"word": "조용히있", "w": 5}, {"word": "가만", "w": 4},
            {"word": "짜져", "w": 5}, {"word": "누워", "w": 4}, {"word": "눕고싶", "w": 5},
            {"word": "집가", "w": 5}, {"word": "집에갈", "w": 5}, {"word": "집감", "w": 5},
            {"word": "각봄", "w": 4}, {"word": "집각", "w": 5}, {"word": "빠져나", "w": 4},
            {"word": "혼밥", "w": 5}, {"word": "혼술", "w": 5}, {"word": "혼영", "w": 5},
            {"word": "조용조용", "w": 4}, {"word": "숨어", "w": 4}, {"word": "숨고싶", "w": 5},
            {"word": "말안", "w": 4}, {"word": "안함", "w": 3}, {"word": "아웃사이더", "w": 5},
            {"word": "쉬는", "w": 5}, {"word": "쉰다", "w": 5}, {"word": "아무", "w": 3},
            {"word": "없이", "w": 3}, {"word": "누워", "w": 4}, {"word": "뒹굴", "w": 4},
            {"word": "넷플", "w": 3}, {"word": "유튜브", "w": 3}, {"word": "잠", "w": 4},
            {"word": "자고", "w": 4}, {"word": "안나가", "w": 5}, {"word": "이불", "w": 4},
            {"word": "평화", "w": 3}, {"word": "만끽", "w": 4}, {"word": "음미", "w": 4},
            {"word": "혼자서", "w": 5}, {"word": "조용히", "w": 4}, {"word": "침착", "w": 3}
        ]
    },
    "SN": {
        "S": [
            {"word": "사실", "w": 5}, {"word": "현실", "w": 4}, {"word": "경험", "w": 4},
            {"word": "직접", "w": 3}, {"word": "구체적", "w": 5}, {"word": "팩트", "w": 3},
            {"word": "실제로", "w": 4}, {"word": "본", "w": 3}, {"word": "들은", "w": 3},
            {"word": "해봤", "w": 4}, {"word": "겪은", "w": 4}, {"word": "당장", "w": 4},
            {"word": "지금", "w": 3}, {"word": "현재", "w": 3}, {"word": "실질적", "w": 5},
            {"word": "실용적", "w": 5}, {"word": "효율적", "w": 4}, {"word": "구체적으로", "w": 5},
            {"word": "정확히", "w": 4}, {"word": "확실히", "w": 4}, {"word": "분명히", "w": 4},
            {"word": "증거", "w": 4}, {"word": "데이터", "w": 4}, {"word": "통계", "w": 4},
            {"word": "실전", "w": 4}, {"word": "실생활", "w": 4}, {"word": "실무", "w": 4},
            {"word": "현장", "w": 4}, {"word": "실체", "w": 4}, {"word": "명확", "w": 4},
            {"word": "세부", "w": 4}, {"word": "디테일", "w": 4}, {"word": "눈에 보이는", "w": 5},
            {"word": "만져본", "w": 4}, {"word": "경험상", "w": 5}, {"word": "과거에", "w": 3},
            {"word": "존예", "w": 4}, {"word": "존잘", "w": 4}, {"word": "존멋", "w": 4},
            {"word": "이쁘", "w": 3}, {"word": "예쁘", "w": 3}, {"word": "예뻐", "w": 3},
            {"word": "살듯", "w": 4}, {"word": "사야", "w": 4}, {"word": "살거", "w": 4},
            {"word": "얼굴", "w": 4}, {"word": "머리", "w": 4}, {"word": "옷", "w": 3},
            {"word": "신발", "w": 3}, {"word": "가방", "w": 3}, {"word": "피부", "w": 3},
            {"word": "먼저", "w": 3}, {"word": "우선", "w": 3}, {"word": "가까운", "w": 4},
            {"word": "봤는데", "w": 4}, {"word": "보이", "w": 3}, {"word": "들리", "w": 3},
            {"word": "집부터", "w": 5}, {"word": "집사", "w": 5}, {"word": "차사", "w": 5},
            {"word": "실제", "w": 4}, {"word": "실물", "w": 4}, {"word": "ㄹㅇ", "w": 4},
            {"word": "리얼", "w": 4}, {"word": "진짜", "w": 3}, {"word": "찐", "w": 4}
        ],
        "N": [
            {"word": "의미", "w": 5}, {"word": "상상", "w": 5}, {"word": "미래", "w": 4},
            {"word": "가능성", "w": 5}, {"word": "만약에", "w": 5}, {"word": "비유", "w": 3},
            {"word": "추상", "w": 4}, {"word": "이론", "w": 4}, {"word": "개념", "w": 4},
            {"word": "아이디어", "w": 5}, {"word": "영감", "w": 5}, {"word": "직관", "w": 4},
            {"word": "느낌", "w": 3}, {"word": "뭔가", "w": 3}, {"word": "어쩌면", "w": 4},
            {"word": "나중에", "w": 3}, {"word": "언젠가", "w": 4}, {"word": "결국", "w": 3},
            {"word": "본질", "w": 5}, {"word": "심층", "w": 4}, {"word": "근본", "w": 4},
            {"word": "철학", "w": 5}, {"word": "깊은", "w": 4}, {"word": "숨은", "w": 4},
            {"word": "패턴", "w": 4}, {"word": "연결", "w": 4}, {"word": "관계", "w": 3},
            {"word": "상징", "w": 4}, {"word": "은유", "w": 4}, {"word": "창의", "w": 5},
            {"word": "혁신", "w": 5}, {"word": "비전", "w": 5}, {"word": "꿈", "w": 4},
            {"word": "이상", "w": 4}, {"word": "통찰", "w": 5}, {"word": "해석", "w": 4},
            {"word": "암시", "w": 4}, {"word": "함의", "w": 5}, {"word": "새로운", "w": 4}
        ]
    },
    "TF": {
        "T": [
            {"word": "이유", "w": 5}, {"word": "원인", "w": 5}, {"word": "논리", "w": 5},
            {"word": "분석", "w": 4}, {"word": "왜", "w": 5}, {"word": "해결", "w": 4},
            {"word": "보험", "w": 5}, {"word": "합리", "w": 5}, {"word": "효율", "w": 4},
            {"word": "객관", "w": 5}, {"word": "판단", "w": 4}, {"word": "평가", "w": 4},
            {"word": "기준", "w": 4}, {"word": "정확", "w": 4}, {"word": "사실", "w": 3},
            {"word": "증명", "w": 4}, {"word": "근거", "w": 5}, {"word": "타당", "w": 5},
            {"word": "논증", "w": 5}, {"word": "결론", "w": 4}, {"word": "추론", "w": 4},
            {"word": "인과", "w": 5}, {"word": "체계", "w": 4}, {"word": "구조", "w": 4},
            {"word": "시스템", "w": 4}, {"word": "방법", "w": 3}, {"word": "전략", "w": 4},
            {"word": "계획적", "w": 4}, {"word": "냉정", "w": 5}, {"word": "냉철", "w": 5},
            {"word": "이성", "w": 5}, {"word": "실리", "w": 4}, {"word": "득실", "w": 5},
            {"word": "손익", "w": 5}, {"word": "따져", "w": 5}, {"word": "계산", "w": 4},
            {"word": "어떻게", "w": 4}, {"word": "방식", "w": 3}, {"word": "수단", "w": 4},
            {"word": "절차", "w": 4}, {"word": "규칙", "w": 4}, {"word": "원리", "w": 4},
            {"word": "법칙", "w": 4}, {"word": "솔직히", "w": 3}, {"word": "어이없", "w": 4},
            {"word": "황당", "w": 4}, {"word": "뭔말", "w": 3}, {"word": "당연", "w": 4},
            {"word": "아니지", "w": 3}, {"word": "팩폭", "w": 5}, {"word": "직설", "w": 5},
            {"word": "퍽이나", "w": 4}, {"word": "웃기", "w": 3}, {"word": "말도안", "w": 4},
            {"word": "대신", "w": 3}, {"word": "해주", "w": 3}, {"word": "개선", "w": 5},
            {"word": "수정", "w": 4}, {"word": "육하원칙", "w": 5}, {"word": "따라", "w": 3},
            {"word": "비효율", "w": 5}, {"word": "최적", "w": 5}, {"word": "다르지않", "w": 4},
            {"word": "에따라", "w": 3},
            {"word": "뭐가", "w": 4}, {"word": "뭔가", "w": 3}, {"word": "어캐", "w": 4},
            {"word": "반박", "w": 5}, {"word": "부들부들", "w": 5}, {"word": "논쟁", "w": 5},
            {"word": "이겼", "w": 4}, {"word": "졌", "w": 4}, {"word": "틀렸", "w": 4},
            {"word": "맞았", "w": 4}, {"word": "팩트체크", "w": 5}, {"word": "팩트", "w": 4},
            {"word": "웃긴게", "w": 4}, {"word": "왤케", "w": 4}, {"word": "왜냐", "w": 5},
            {"word": "힘드노", "w": 4}, {"word": "뭐노", "w": 4}, {"word": "어쩔", "w": 3},
            {"word": "지는건", "w": 4}, {"word": "못함", "w": 3}, {"word": "못해", "w": 3},
            {"word": "안됨", "w": 3}, {"word": "안돼", "w": 3}, {"word": "별론데", "w": 4},
            {"word": "솔까", "w": 4}, {"word": "솔직", "w": 4}, {"word": "직빵", "w": 4},
            {"word": "걍", "w": 2}, {"word": "그래서", "w": 3}, {"word": "그러니까", "w": 4}
        ],
        "F": [
            {"word": "기분", "w": 5}, {"word": "마음", "w": 5}, {"word": "공감", "w": 5},
            {"word": "서운", "w": 4}, {"word": "감정", "w": 5}, {"word": "속상", "w": 5},
            {"word": "어떡해", "w": 5}, {"word": "느낌", "w": 4}, {"word": "감성", "w": 5},
            {"word": "정서", "w": 4}, {"word": "위로", "w": 5}, {"word": "힐링", "w": 5},
            {"word": "따뜻", "w": 4}, {"word": "배려", "w": 5}, {"word": "존중", "w": 4},
            {"word": "이해", "w": 4}, {"word": "고민", "w": 4}, {"word": "걱정", "w": 4},
            {"word": "불안", "w": 4}, {"word": "슬픔", "w": 4}, {"word": "기쁨", "w": 3},
            {"word": "행복", "w": 3}, {"word": "사랑", "w": 4}, {"word": "좋아", "w": 3},
            {"word": "싫어", "w": 3}, {"word": "화나", "w": 4}, {"word": "짜증", "w": 4},
            {"word": "답답", "w": 4}, {"word": "억울", "w": 5}, {"word": "미안", "w": 4},
            {"word": "고마", "w": 4}, {"word": "감동", "w": 5}, {"word": "눈물", "w": 5},
            {"word": "울", "w": 4}, {"word": "아픔", "w": 4}, {"word": "상처", "w": 5},
            {"word": "치유", "w": 5}, {"word": "마음이", "w": 5}, {"word": "가슴", "w": 4},
            {"word": "심정", "w": 5}, {"word": "감정적", "w": 5}, {"word": "인간적", "w": 5},
            {"word": "따뜻한", "w": 5}, {"word": "공감해", "w": 5}, {"word": "위로해", "w": 5},
            {"word": "힘들", "w": 4}, {"word": "안쓰러", "w": 5}, {"word": "불쌍", "w": 4},
            {"word": "측은", "w": 5}, {"word": "기뻐", "w": 4}, {"word": "진심", "w": 4},
            {"word": "우울", "w": 5}, {"word": "힘내", "w": 5}, {"word": "괜찮", "w": 4},
            {"word": "응원", "w": 5}, {"word": "착하", "w": 3},
            {"word": "본인이", "w": 5}, {"word": "좋으면", "w": 4}, {"word": "됐지", "w": 4},
            {"word": "본인맘", "w": 5}, {"word": "알아서", "w": 3}, {"word": "맘대로", "w": 4},
            {"word": "그래됐", "w": 4}, {"word": "어쩔수없", "w": 4}, {"word": "받아들", "w": 4},
            {"word": "이해해", "w": 5}, {"word": "이해함", "w": 5}, {"word": "그럴수", "w": 4},
            {"word": "ㅠㅠ", "w": 5}, {"word": "ㅜㅜ", "w": 5}, {"word": "ㅎㅎ", "w": 3},
            {"word": "ㅋㅋ", "w": 2}, {"word": "잘됐", "w": 4}, {"word": "잘했", "w": 4},
            {"word": "고생", "w": 4}, {"word": "수고", "w": 4}, {"word": "안아줘", "w": 5},
            {"word": "토닥", "w": 5}, {"word": "ㅇㅋ", "w": 3}, {"word": "오키", "w": 3},
            {"word": "ㅇㅇ", "w": 2}, {"word": "알겠", "w": 3}, {"word": "화이팅", "w": 5},
            {"word": "파이팅", "w": 5}, {"word": "존버", "w": 4}, {"word": "아쉽", "w": 4}
        ]
    },
    "JP": {
        "J": [
            {"word": "계획", "w": 5}, {"word": "정리", "w": 4}, {"word": "미리", "w": 5},
            {"word": "확정", "w": 4}, {"word": "리스트", "w": 5}, {"word": "예약", "w": 4},
            {"word": "스케줄", "w": 5}, {"word": "일정", "w": 5}, {"word": "체크", "w": 4},
            {"word": "준비", "w": 4}, {"word": "사전", "w": 4}, {"word": "미리미리", "w": 5},
            {"word": "예정", "w": 4}, {"word": "정해", "w": 4}, {"word": "결정", "w": 4},
            {"word": "확실", "w": 4}, {"word": "정확", "w": 3}, {"word": "명확", "w": 3},
            {"word": "체계", "w": 4}, {"word": "순서", "w": 4}, {"word": "단계", "w": 4},
            {"word": "규칙", "w": 4}, {"word": "원칙", "w": 4}, {"word": "기준", "w": 3},
            {"word": "정돈", "w": 4}, {"word": "정렬", "w": 4}, {"word": "분류", "w": 4},
            {"word": "마감", "w": 4}, {"word": "데드라인", "w": 5}, {"word": "기한", "w": 4},
            {"word": "시간 맞춰", "w": 5}, {"word": "약속 시간", "w": 5}, {"word": "정시", "w": 4},
            {"word": "체크리스트", "w": 5}, {"word": "투두", "w": 5}, {"word": "할 일", "w": 4},
            {"word": "완료", "w": 3}, {"word": "마무리", "w": 4}, {"word": "끝내", "w": 3},
            {"word": "깔끔", "w": 4}, {"word": "정확히", "w": 4}, {"word": "틀림없이", "w": 4},
            {"word": "어디로", "w": 4}, {"word": "갈건데", "w": 4}, {"word": "정해야", "w": 5},
            {"word": "계획짜", "w": 5}, {"word": "짜야지", "w": 5}, {"word": "어캐할지", "w": 5},
            {"word": "만나기전", "w": 5}, {"word": "전에", "w": 3}, {"word": "해야지", "w": 4},
            {"word": "해야함", "w": 4}, {"word": "해야해", "w": 4}, {"word": "해야됨", "w": 4},
            {"word": "정하고", "w": 4}, {"word": "정한", "w": 4}, {"word": "알아보", "w": 4},
            {"word": "찾아보", "w": 4}, {"word": "검색", "w": 4}, {"word": "확인", "w": 4},
            {"word": "일주일", "w": 3}, {"word": "먼저정", "w": 5}, {"word": "미리정", "w": 5}
        ],
        "P": [
            {"word": "즉흥", "w": 5}, {"word": "그때", "w": 4}, {"word": "유연", "w": 4},
            {"word": "대충", "w": 4}, {"word": "일단", "w": 5}, {"word": "상황 봐서", "w": 4},
            {"word": "나중에", "w": 4}, {"word": "천천히", "w": 3}, {"word": "여유", "w": 4},
            {"word": "자유", "w": 4}, {"word": "편한", "w": 3}, {"word": "느긋", "w": 4},
            {"word": "막", "w": 4}, {"word": "아무", "w": 3}, {"word": "뭐든", "w": 4},
            {"word": "그냥", "w": 3}, {"word": "그렇게", "w": 2}, {"word": "알아서", "w": 4},
            {"word": "흐름", "w": 4}, {"word": "타이밍", "w": 4}, {"word": "순간", "w": 3},
            {"word": "융통", "w": 5}, {"word": "임기응변", "w": 5}, {"word": "애드립", "w": 5},
            {"word": "변화", "w": 3}, {"word": "적응", "w": 4}, {"word": "조절", "w": 3},
            {"word": "바꿔", "w": 3}, {"word": "다시", "w": 2}, {"word": "또", "w": 2},
            {"word": "나중", "w": 4}, {"word": "미루", "w": 5}, {"word": "일단은", "w": 5},
            {"word": "가다가", "w": 4}, {"word": "보면서", "w": 4}, {"word": "지금은", "w": 3},
            {"word": "당장", "w": 3}, {"word": "급하게", "w": 3}, {"word": "여유롭게", "w": 4},
            {"word": "막상", "w": 4}, {"word": "생각나면", "w": 4}, {"word": "끌리면", "w": 4},
            {"word": "하고 싶을 때", "w": 5}, {"word": "기분 내킬 때", "w": 5},
            {"word": "시켰으니", "w": 4}, {"word": "먹긴해", "w": 4}, {"word": "별로여도", "w": 4},
            {"word": "자연스럽", "w": 5}, {"word": "흘러가", "w": 5}, {"word": "기다려", "w": 4},
            {"word": "봐야지", "w": 4}, {"word": "해봐야", "w": 4}, {"word": "머", "w": 3},
            {"word": "뭐", "w": 3}, {"word": "별로", "w": 3}, {"word": "상관없", "w": 4},
            {"word": "됐어", "w": 3}, {"word": "ㅇㅋ", "w": 3}, {"word": "괜찮", "w": 3},
            {"word": "어쩔수없", "w": 4}, {"word": "어쩔", "w": 3}, {"word": "몰라", "w": 4},
            {"word": "글쎄", "w": 4}, {"word": "모르겠", "w": 4}, {"word": "됐지", "w": 4}
        ]
    }
}

DESCRIPTIONS = {
    "ISTP": {"title": "만능 재주꾼", "traits": ["#냉철함", "#해결사"], "desc": "사고 현장에서도 수리비부터 계산할 쿨한 해결사군요!"},
    "ENFP": {"title": "재기발랄한 활동가", "traits": ["#에너지", "#인싸"], "desc": "세상을 즐거움으로 채우는 당신은 자유로운 영혼입니다!"},
}


def get_dimension_for_question(question_index: int) -> str:
    if question_index < 3:
        return "EI"
    elif question_index < 6:
        return "SN"
    elif question_index < 9:
        return "TF"
    else:
        return "JP"


# ==========================================================
# 2. 로직 영역 (정밀 필터링 및 가중치 누적 강화)
# ==========================================================

def analyze_linguistic_detail(ans: str, dim: str, scores: dict):
    """
    [정밀 언어 분석 필터] - 기준 완화 및 로직 강화 버전
    """
    if not isinstance(ans, str) or not ans: return

    ans_len = len(ans.replace(" ", ""))  # 공백 제외 글자 수로 변경 (더 정확함)
    clean_ans = ans.strip()

    # --- [EI] 에너지 방향성 ---
    if dim == "EI":
        # E: 긴 문장, 활기찬 부호
        if ans_len > 30: scores["E"] += 2  # 기준 40 -> 30으로 완화
        if "!" in clean_ans or "~" in clean_ans: scores["E"] += 1
        if "ㅋㅋ" in clean_ans or "ㅎㅎ" in clean_ans: scores["E"] += 1

        # I: 짧은 문장, '없'는 부정어, 쉼
        # "아무 스케줄 없이 푹 쉬는 하루" -> 공백 제외 12글자 -> 이제 걸림!
        if ans_len < 15: scores["I"] += 2
        if clean_ans.endswith(".") or clean_ans.endswith("요"): scores["I"] += 1

        # [추가] 소극적/부정적 표현은 I일 확률 높음
        if re.search(r"없|안|못|아무", clean_ans): scores["I"] += 1

    # --- [SN] 인식 방식 (들여쓰기 수정 완료) ---
    if dim == "SN":
        # 1. [S] 숫자와 단위 = 현실 감각
        # 예: "3개", "10분", "만원"
        if re.search(r"[0-9]+|일|월|년|개|번|시|분|원", clean_ans):
            scores["S"] += 2

        # 2. [S] 과거 시제/완료형 = 직접 경험한 사실
        # 예: "먹었어", "갔다왔어", "봤어" -> 경험 기반(S)
        if re.search(r"았|었|했|봤|갔|왔", clean_ans):
            scores["S"] += 1.5

        # 3. [N] 비유적 표현 (직유/은유)
        # 예: "마치 구름 같아", "그림처럼 예뻐"
        if re.search(r"마치|~처럼|~같이|~양|듯한", clean_ans):
            scores["N"] += 3  # 비유는 N의 강력한 신호

        # 4. [N] 불확실/추측/미래 시제
        # 예: "일 것 같아", "아마도", "그러지 않을까?"
        if re.search(r"것 같|을까|겠지|지도|아마|혹시", clean_ans):
            scores["N"] += 2

        # 5. [N] 모호한 수식어
        # 예: "뭔가 느낌이", "약간 그런 거"
        if re.search(r"뭔가|약간|묘한|이상한|그런", clean_ans):
            scores["N"] += 1

    # --- [TF] 판단 근거 (들여쓰기 수정 완료) ---
    if dim == "TF":
        # 1. [T] 의문문과 인과관계 (따지는 말투)
        # 예: "왜?", "그래서?", "근데 그게 맞아?"
        if "?" in clean_ans:
            scores["T"] += 1.5
        if "왜" in clean_ans and "?" in clean_ans:  # "왜?" 콤보는 강력한 T
            scores["T"] += 2

        # 2. [T] 논리적 접속사
        # 예: "근데", "하지만", "그러니까", "결국"
        if re.search(r"근데|하지만|그래서|그러니까|결국|즉", clean_ans):
            scores["T"] += 1.5

        # 3. [T] 단정적/건조한 어미
        # 예: "~다.", "~함.", "~임.", "~지."
        if re.search(r"(다|함|임|지|까)(\.|!|$)", clean_ans):
            scores["T"] += 1

        # 4. [F] 감탄사와 이모티콘 (풍부한 리액션)
        # 예: "!", "ㅠㅠ", "ㅎㅎㅎ", "♥"
        if re.search(r"!|♥|♡", clean_ans):
            scores["F"] += 1.5
        if re.search(r"[ㅠㅜㅎㅋ]{2,}", clean_ans):  # 2글자 이상 연속 (ㅠㅠ, ㅋㅋ)
            scores["F"] += 2

        # 5. [F] 공감/부드러운 어미
        # 예: "~구나", "~네요", "~가요", "~잖아요"
        if re.search(r"구나|네요|아요|어요|죠|잖아요", clean_ans):
            scores["F"] += 1.5

        # 6. [F] 길게 끄는 말투 (감정의 여운)
        # 예: "아~~~", "진짜...", "그렇구나..."
        if re.search(r"~|\.\.|[아어으]{2,}", clean_ans):  # 모음 길게(아아아)
            scores["F"] += 1.5

    # --- [JP] 생활 양식 (들여쓰기 수정 완료) ---
    if dim == "JP":
        if re.search(r"해야|할게|하자|필수|꼭|계획", clean_ans): scores["J"] += 2
        if re.search(r"글쎄|아마|몰라|일단|그냥|봐서", clean_ans): scores["P"] += 2


# ==========================================================
# [수정] 3. 분석 로직 (미감지 시 N+1 보정 추가)
# ==========================================================

def calculate_partial_mbti(answers: list):
    scores = {k: 0 for k in "EISNTFJP"}

    for i, ans in enumerate(answers):
        target_dim = get_dimension_for_question(i)

        # 안전한 문자열 처리
        if not isinstance(ans, str) or not ans: continue

        # [플래그] 이번 답변이 키워드나 패턴에 걸렸는지 확인
        is_detected = False

        # 1. 전차원 교차 분석 (Dictionary Scanning)
        for dim_key, traits in DICTIONARY.items():
            for trait, keyword_list in traits.items():
                for k in keyword_list:
                    if k["word"] in ans:
                        scores[trait] += k["w"]
                        is_detected = True  # 감지됨!

        # 2. 정규식 패턴 분석 (Regex Scanning)
        # [SN]
        if re.search(r"만약에|~라면|상상|미래|혹시|가정|세계관", ans):
            scores["N"] += 3;
            is_detected = True
        # [S] 오감(시각,미각 등)을 나타내는 표현 + 현실 인식
        if re.search(r"맛있|배고파|색깔|냄새|소리|보여|들려|아파|추워|더워|현실|당장|팩트|실제", ans):
            scores["S"] += 3;
            is_detected = True

        # [TF]
        # T: 원인 분석 및 해결책 제시
        if re.search(r"왜|이유|원인|논리|따져|생각해|해결|방법", ans):
            scores["T"] += 4;
            is_detected = True
        # F: 감정 이입 및 리액션
        if re.search(r"속상|서운|어떡해|마음|괜찮|좋겠|대박|헐|진짜|기쁨|행복", ans):
            scores["F"] += 4;
            is_detected = True

        # [JP]
        if re.search(r"계획|미리|체크|일정", ans):
            scores["J"] += 3;
            is_detected = True
        if re.search(r"봐서|그때|일단|그냥", ans):
            scores["P"] += 3;
            is_detected = True

        # =======================================================
        # [NEW] 3. 최후의 보루: 아무것도 안 잡혔으면 N(추상) +1
        # =======================================================
        if not is_detected:
            # "뭔가 감지가 안 되는 묘한 답변 -> 추상적(N)일 확률 높음"
            scores["N"] += 1

        # 4. 정밀 언어 분석 (보정은 보정대로 계속 수행)
        # (N+1을 받았더라도, 말투에서 I나 P가 감지될 수 있으므로 수행)
        analyze_linguistic_detail(ans, "EI", scores)
        analyze_linguistic_detail(ans, "SN", scores)
        analyze_linguistic_detail(ans, "TF", scores)
        analyze_linguistic_detail(ans, "JP", scores)

    # 결과 문자열 계산 (기존과 동일)
    partial_mbti = ""
    if answers:
        if len(answers) >= 3:
            partial_mbti += ("E" if scores["E"] >= scores["I"] else "I")
        else:
            partial_mbti += "X"
        if len(answers) >= 6:
            partial_mbti += ("S" if scores["S"] >= scores["N"] else "N")
        else:
            partial_mbti += "X"
        if len(answers) >= 9:
            partial_mbti += ("T" if scores["T"] >= scores["F"] else "F")
        else:
            partial_mbti += "X"
        if len(answers) >= 12:
            partial_mbti += ("J" if scores["J"] >= scores["P"] else "P")
        else:
            partial_mbti += "X"
    else:
        partial_mbti = "XXXX"

    return {"mbti": partial_mbti, "scores": scores}


# [수정됨] 중복 정의 제거하고 하나로 합침
def analyze_single_answer(answer: str, dimension: str) -> dict:
    """단일 답변 분석: 키워드 + 패턴 + 정밀분석 + N+1 보정 점수를 모두 합산하여 반환"""
    scores = {k: 0 for k in dimension}  # 예: {'E':0, 'I':0}
    is_detected = False  # 감지 플래그

    # 1. 키워드
    if dimension in DICTIONARY:
        for trait, keywords in DICTIONARY[dimension].items():
            for k in keywords:
                if k["word"] in answer:
                    scores[trait] += k["w"]
                    is_detected = True

    # 2. 정규식 패턴 (N+1 보정을 위해 감지 여부 체크)
    if dimension == "SN":
        if re.search(r"만약에|~라면|상상|미래|혹시", answer): scores["N"] += 3; is_detected = True
        if re.search(r"현실|당장|팩트|실제", answer): scores["S"] += 3; is_detected = True
    if dimension == "TF":
        if re.search(r"왜|이유|논리|따져", answer): scores["T"] += 4; is_detected = True
        if re.search(r"속상|서운|어떡해|마음", answer): scores["F"] += 4; is_detected = True
    if dimension == "JP":
        if re.search(r"계획|체크|리스트|시간", answer): scores["J"] += 3; is_detected = True
        if re.search(r"봐서|그때|일단|그냥", answer): scores["P"] += 3; is_detected = True

    # 3. [최후의 보루] 미감지 시 N+1 (SN 차원 질문이 아니더라도 N 점수 부여)
    # 단일 차원 분석이므로 'N'이 있는 dimension(SN)일 때만 적용하는 것이 논리적임
    if not is_detected and "N" in scores:
        scores["N"] += 1

    # 4. [중요] 정밀 언어 분석 (무조건 실행하여 1~2점 누적)
    analyze_linguistic_detail(answer, dimension, scores)

    # 점수 계산
    trait1, trait2 = tuple(dimension)
    score1 = scores.get(trait1, 0)
    score2 = scores.get(trait2, 0)

    side = trait1 if score1 >= score2 else trait2
    score = score1 if score1 >= score2 else score2

    return {"scores": scores, "side": side, "score": score}


def run_analysis(answers: list):
    """전체 분석 실행"""
    result = calculate_partial_mbti(answers)
    scores = result["scores"]

    # MBTI 결과 (X 제거)
    res_mbti = result["mbti"].replace("X", "")

    # 만약 답변 부족으로 X가 있다면 강제로 계산
    if len(res_mbti) < 4:
        res_mbti = (
                ("E" if scores["E"] >= scores["I"] else "I") +
                ("S" if scores["S"] >= scores["N"] else "N") +
                ("T" if scores["T"] >= scores["F"] else "F") +
                ("J" if scores["J"] >= scores["P"] else "P")
        )

    def get_conf(a, b):
        total = a + b + 0.1  # 0나누기 방지
        return round((abs(a - b) / total) * 100, 1)

    confidence = {
        "EI": get_conf(scores["E"], scores["I"]),
        "SN": get_conf(scores["S"], scores["N"]),
        "TF": get_conf(scores["T"], scores["F"]),
        "JP": get_conf(scores["J"], scores["P"])
    }

    return res_mbti, scores, confidence