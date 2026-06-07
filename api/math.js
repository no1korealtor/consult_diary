export const config = {
  runtime: 'edge', 
};

export default async function handler(req) {
  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ message: 'POST 요청만 지원합니다.' }), { status: 405 });
  }

  try {
    const body = await req.json();
    const word = body.word;

    if (!word) {
      return new Response(JSON.stringify({ message: '단어(word)가 필요합니다.' }), { status: 400 });
    }

    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return new Response(JSON.stringify({ message: 'API 키가 설정되지 않았습니다.' }), { status: 500 });
    }

    const prompt = `너는 중학교 2학년 1학기 기초가 많이 부족한 아이를 가르치는 다정하고 친절한 수학 선생님이야. 
아이가 '${word}'에 대한 기초 문제를 풀고 싶어해. 
이 개념을 확인할 수 있는 아주 쉽고 기본적인 기초 문제 딱 1개만 내줘. 꼬아낸 응용 문제는 절대 안돼.
해설은 왜 이렇게 계산해야 하는지 초등학생에게 설명하듯 다정하게 하나씩 풀어서 설명해줘.
중요: 분수, 거듭제곱(제곱), 곱하기 기호 등 모든 수식은 반드시 LaTeX 문법으로 작성하고 양쪽을 $ 기호로 감싸줘. (예: $x^2$, $\\frac{1}{2}$, $a \\times b$).
응답은 반드시 아래 JSON 형식으로만 줘. 절대 다른 말은 붙이지 마:
{"problem": "문제 내용", "answer": "정답", "solution": "풀이 과정"}`;

    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { response_mime_type: "application/json" }
        })
    });

    if (!response.ok) {
        throw new Error(`API 응답 오류: ${response.status}`);
    }

    const data = await response.json();
    let resultJson = {};
    if (data.candidates && data.candidates[0].content.parts[0].text) {
        resultJson = JSON.parse(data.candidates[0].content.parts[0].text);
    } else {
        throw new Error("Invalid response from Gemini");
    }

    return new Response(JSON.stringify(resultJson), { status: 200, headers: { 'Content-Type': 'application/json' } });

  } catch (error) {
    console.error('AI 문제 생성 오류:', error);
    return new Response(JSON.stringify({ message: '서버 오류', error: error.message }), { status: 500 });
  }
}
