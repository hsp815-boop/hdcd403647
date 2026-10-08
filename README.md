# 상담 워크룸 · Streamlit 배포용

이 폴더만 Streamlit Community Cloud에 배포하면 됩니다.

## 배포

1. 이 폴더의 파일을 GitHub 저장소에 올립니다. 저장소 루트가 상위 폴더라면 앱 파일 경로는 `streamlit_deploy/app.py`입니다.
2. Streamlit에서 저장소와 앱 파일을 연결합니다.
3. 앱 설정의 **Secrets**에 아래 항목을 추가하고 배포합니다.

```toml
OPENAI_API_KEY = "발급받은_API_키"
```

앱은 OpenAI Responses API와 `gpt-6-luna` 모델을 사용합니다. 배포용 API 키는 코드나 `.env`에 넣지 말고 Streamlit Secrets에 등록하세요.

## 파일

- `app.py`: Streamlit 화면
- `core.py`: Responses API, 검색, 자료 저장
- `policy_samples.py`, `case_samples.py`, `sample_files.py`: 샘플 데이터와 테스트 자료 내려받기
- `style.css`: 화면 스타일
- `requirements.txt`: Python 패키지
- `.streamlit/config.toml`: 테마와 업로드 설정

데이터베이스는 처음 실행할 때 `data/assistant.db`에 자동 생성됩니다. Streamlit Community Cloud의 로컬 파일은 앱 재배포·재시작에 따라 유지되지 않을 수 있습니다. 운영 자료의 장기 보관이 필요하면 외부 데이터베이스 연결을 별도로 구성하세요.

## 로컬 실행

```powershell
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# .env에 OPENAI_API_KEY를 입력한 뒤
streamlit run app.py
```
