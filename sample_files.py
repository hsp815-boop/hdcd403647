"""Portable download pack containing only fictional test records."""
import io
import zipfile
import core
import policy_samples

def download_pack():
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('README.txt','체험용 가상 데이터입니다. 실제 업무 정책이 아닙니다.\nKMS 10개와 이전 협의서 12개를 포함합니다.\nKMS 검색·등록에는 kms 폴더의 TXT 파일만 올리세요.\n협의서는 소개의 가상 예시 등록 버튼으로 앱에 추가할 수 있습니다.\nCSV는 전체 샘플 목록 확인용입니다.\n')
        z.writestr('test_data.csv',core.export_csv(policy_samples.SAMPLES))
        for kind,folder in [('KMS','kms'),('협의서','previous_cases')]:
            for i,r in enumerate((r for r in policy_samples.SAMPLES if r['kind']==kind),1):
                text=f"[문서 제목]\n{r['title']}\n\n[자료 기준일]\n{r['effective']}\n\n{r['body']}"
                z.writestr(f'{folder}/{folder}_{i:02d}.txt',text.encode('utf-8-sig'))
    return out.getvalue()
