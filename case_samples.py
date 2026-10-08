"""Twelve fictional prior consultation documents, distinct from KMS policies."""
import core

FIELDS=['업무 분류','협의서 번호','담당 부서','고객 요청','확인 내용','회신 내용','처리 결과','참고 업무 기준','유의사항']
def body(values):
    return '\n\n'.join(f'[{label}]\n{value}' for label,value in zip(FIELDS,values))

CATEGORIES=['결제·청구','카드 관리','이용한도','결제·청구','해외 이용','결제·청구','자동납부','명세서','포인트·마일리지']
SAMPLES=[]
LEGACY=[]
for i,(title,kind,text) in enumerate(x for x in core.SAMPLES if x[1]=='협의서'):
    LEGACY.append(dict(title=title,body=text))
    question,answer=text.split('\n답변: ',1)
    SAMPLES.append(dict(title=title,kind='협의서',effective=f'2026-01-{i+5:02d}',reviewed=True,
        body=body([CATEGORIES[i],f'DEMO-2026-{i+1:03d}','가상 상담지원부',question.removeprefix('질문: '),
        '본인 확인 및 해당 거래·접수 상태 확인이 필요함.',answer,'확인 후 회신 또는 담당 부서 검토 요청. 실제 처리는 수행하지 않은 가상 사례.',
        '관련 KMS 업무 기준과 시스템 상태를 함께 확인하세요.','과거 개별 사례이며 일반 업무 기준으로 적용할 수 없습니다. 체험용 가상 협의서입니다.'])))

for i,(title,request,checks,reply) in enumerate([
    ('마일리지 전환 한도 초과 협의서','고객이 6만 마일리지 전환을 신청했습니다.',
     '예시 업무 기준의 한도는 5만 마일리지. 한도 산정 기간과 기존 전환 내역은 별도 확인 필요.',
     '예시 한도를 초과하는 요청임을 안내하고, 산정 기간·기존 전환 내역을 확인한 뒤 신청 가능 범위를 회신하기로 했습니다. 분할 신청으로 한도를 우회할 수 있다고 안내하지 않았습니다.'),
    ('마일리지 제휴 회원 정보 확인 협의서','포인트 전환 신청 고객의 제휴 회원 정보가 확인되지 않습니다.',
     '고객 본인과 제휴 회원 정보, 정보 불일치 원인을 확인해야 합니다.',
     '회원 정보 확인 전에는 신청 완료로 안내하지 않고, 담당 부서에서 등록 정보와 제휴사 적용 조건을 확인한 후 재접수 가능 여부를 회신하기로 했습니다.'),
    ('마일리지 전환 포인트 잔액 확인 협의서','고객이 잔여 포인트보다 많은 수량의 전환을 요청했습니다.',
     '실제 잔여 포인트, 전환 비율, 최소 단위와 신청 조건을 확인해야 합니다. 비율은 예시에서 정의하지 않았습니다.',
     '확인된 잔여 포인트와 실제 업무 기준을 조회하여 전환 가능 수량을 안내하기로 했습니다. 확인되지 않은 전환 비율이나 적립 완료일을 제시하지 않았습니다.')
],10):
    SAMPLES.append(dict(title='[가상 예시] '+title,kind='협의서',effective=f'2026-02-{i-9:02d}',reviewed=True,
        body=body(['포인트·마일리지',f'DEMO-2026-{i:03d}','가상 포인트운영부',request,checks,reply,
        '확인 및 담당 부서 회신 대기 (가상 사례)','[가상 예시] 포인트 → 마일리지 전환 업무 기준',
        '체험용 가상 협의서입니다. 실제 고객 정보는 없으며 일반 정책을 확정하는 근거가 아닙니다.'])))

def seed():
    migrated=added=0
    for row in core.sources():
        if row['kind']=='협의서' and any(row['title']==r['title'] and row['body']==r['body'] for r in LEGACY):
            new=next(r for r in SAMPLES if r['title']==row['title'])
            core.edit_source(row['id'],row['title'],'협의서',new['body'],new['effective'],bool(row['reviewed']))
            migrated+=1
    for r in SAMPLES:
        if core.add_source(r['title'],r['kind'],r['body'],r['effective'],True):added+=1
    return migrated,added
