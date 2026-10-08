"""Clearly fictional operational standards; never migrate user-created records."""
import core
import case_samples

LEGACY = [dict(title=t, kind=k, body=b) for t,k,b in core.SAMPLES if k=='KMS']
FIELDS = ['업무 분류','담당 부서','문서 버전','업무 개요','적용 대상','한도 및 조건','신청 및 처리 방법','처리 시점','유의사항','참고 문서']
TARGETS = ['결제일 변경 신청 고객','카드 분실 신고 고객','이용한도 변경 신청 고객','결제 취소 확인 요청 고객','해외 이용 금액 확인 요청 고객','일시불 거래 할부 전환 신청 고객','카드 자동납부 신청 고객','이용명세서 재발송 요청 고객','포인트 적립 확인 요청 고객']
CATEGORIES = ['결제·청구','카드 관리','이용한도','결제·청구','해외 이용','결제·청구','자동납부','명세서','포인트·마일리지']

def body(values):
    return '\n\n'.join(f'[{label}]\n{value}' for label,value in zip(FIELDS,values))

SAMPLES = []
index = 0
for title,kind,text in core.SAMPLES:
    if kind=='KMS':
        method=text.split('답변: ',1)[-1]
        text=body([CATEGORIES[index],'가상 업무운영부','예시 v1.0',title.replace('[가상 예시] ',''),TARGETS[index],
                   '구체적인 한도·비용·가능 여부는 승인된 업무 기준 및 시스템에서 확인',method,
                   '시스템 및 담당 부서 확인 후 안내','체험용 가상 기준입니다. 실제 업무에 적용하지 마세요.','실제 참고 문서 미등록'])
        index+=1
    SAMPLES.append(dict(title=title,kind=kind,body=text,effective='2026-01-01',reviewed=True))
SAMPLES.insert(0,dict(title='[가상 예시] 포인트 → 마일리지 전환 업무 기준',kind='KMS',effective='2026-01-01',reviewed=True,
    body=body(['포인트·마일리지','가상 포인트운영부','예시 v1.0','고객의 포인트를 제휴 마일리지로 전환하는 신청 업무',
    '본인 확인 및 제휴 회원 정보 확인을 마친 전환 신청 고객',
    '전환 한도: 5만 마일리지 (사용자가 제공한 예시 값). 한도 산정 기간·전환 비율·최소 단위는 미정으로 확인 필요.',
    '예시 절차: 본인 확인 → 제휴 회원 정보 및 잔여 포인트 확인 → 전환 조건 안내 → 고객 동의 확인 → 신청 접수. 실제 접수 채널과 시스템 경로는 담당 부서 확인 필요.',
    '적립 완료 시점은 미정. 확인 전에는 완료일을 확정하여 안내하지 않음.',
    '취소 가능 여부·이름 일치 조건·제휴사별 제한은 확인 필요. 가상 예시이며 실제 승인된 업무 기준이 아닙니다.',
    '실제 사내 공지·업무 매뉴얼을 연결해 사용하세요.'])))

def migrate_known_samples():
    changed=0
    for r in core.sources():
        old=next((x for x in LEGACY if x['title']==r['title'] and x['body']==r['body'] and r['kind']=='KMS'),None)
        if old:
            replacement=next(x for x in SAMPLES if x['title']==r['title'])
            core.edit_source(r['id'],r['title'],'KMS',replacement['body'],r['effective'],bool(r['reviewed']))
            changed+=1
    example=SAMPLES[0]
    core.add_source(example['title'],example['kind'],example['body'],example['effective'],True)
    return changed

# The current demo pack contains ten operational standards and twelve prior cases.
SAMPLES=[r for r in SAMPLES if r['kind']=='KMS']+case_samples.SAMPLES
