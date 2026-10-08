from pathlib import Path
from datetime import date
import json
import pandas as pd
import streamlit as st
import core
import policy_samples
import sample_files

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Luna · 협의서 답변 도우미',layout='wide',initial_sidebar_state='collapsed')
st.markdown(f"<style>{(ROOT/'style.css').read_text(encoding='utf-8')}</style>",unsafe_allow_html=True)
st.markdown('<div class="brand">luna<span>.</span><small>협의서 · KMS 답변 도우미</small></div>',unsafe_allow_html=True)
st.title('답변의 근거를 찾고, 검토까지 한곳에서.')
st.write('과거 협의서와 업무 기준을 찾아 답변 초안을 만들고, 검토한 지식을 다음 문의에 활용하세요.')
if 'generation' not in st.session_state: st.session_state.generation=0
if 'pending_question' in st.session_state:
    st.session_state.question=st.session_state.pop('pending_question')
if st.session_state.pop('enable_samples_next',False):
    st.session_state.include_samples=True
rows=core.sources()
with st.sidebar:
    st.header('작업 환경')
    st.caption(f'OpenAI Responses API · {core.MODEL}')
    st.success('API 키 준비 완료' if core.key() else 'API 키 설정 필요')
    st.toggle('가상 예시 자료도 검색',key='include_samples')
    st.caption('문의와 검색된 근거를 OpenAI로 전송합니다. 자료 등록·검색·저장은 로컬에서 처리합니다.')
    st.caption('저장 위치: data/assistant.db')
    st.caption('배포 시 앱 설정의 Secrets에 OPENAI_API_KEY를 등록하세요.')
    st.caption('사내 KMS와 자동 연동하지 않습니다. 등록용 CSV를 내려받아 활용하세요.')
eligible=[r for r in rows if st.session_state.include_samples or not r['title'].startswith('[가상 예시]')]
tabs=st.tabs(['소개','협의서 답변 작성','KMS 검색·등록','협의서 검색'])

with tabs[0]:
    st.subheader('자료를 찾는 시간은 줄이고, 판단은 직접 하세요.')
    st.write('자료 등록 → 관련 근거 검색 → AI 초안 작성 → 담당자 검토·저장 순서로 진행합니다.')
    st.markdown('**협의서 답변 작성**에서는 기존 사례와 KMS를 함께 참고합니다. **KMS 검색·등록**에서는 업무 기준을 관리하고, **협의서 검색**에서는 이전 고객 요청과 회신 사례를 조회합니다.')
    st.info(f"등록 자료 {len(rows)}개 · 검토 완료·사용 중 {sum(r['active'] and r['reviewed'] for r in rows)}개 · 저장된 답변 {len(core.history())}개")
    with st.expander('처음 사용한다면'):
        st.write('KMS 검색·등록 탭에서 자료를 올리거나 내용을 붙여 넣으세요. 기준일과 검토 완료 여부를 확인해야 답변 근거로 검색됩니다.')
        st.write('텍스트 PDF·DOCX·XLSX·CSV·TXT·MD를 지원합니다. 스캔 PDF와 HWP는 텍스트로 변환해 등록하세요. 업로드한 원본은 수정하지 않습니다.')
        st.write('가상 예시는 기능 체험용이며 실제 회사 정책이 아닙니다.')
    if st.button(f'가상 예시 자료 {len(policy_samples.SAMPLES)}개 등록'):
        for sample in policy_samples.SAMPLES: core.add_source(sample['title'],sample['kind'],sample['body'],sample['effective'],True)
        st.session_state.enable_samples_next=True
        st.rerun()
    st.download_button('테스트 데이터 다운받기',sample_files.download_pack(),file_name='consultation_test_data.zip',mime='application/zip',width='stretch')
    st.caption('KMS 10개와 이전 협의서 12개를 제공합니다. ZIP의 kms 폴더에 있는 TXT 파일로 KMS 업로드를 테스트하세요.')
    st.caption('등록 데이터와 검토 이력은 앱을 재시작해도 유지됩니다. 작업 중인 미저장 초안은 현재 브라우저 세션에만 유지됩니다.')

with tabs[1]:
    left,right=st.columns([1,1.15],gap='large')
    with left:
        st.subheader('새 문의')
        question=st.text_area('상담원 질문 또는 협의서 내용',height=180,placeholder='상황, 고객 요청, 확인한 내용과 답변이 필요한 부분을 입력하세요.',key='question',max_chars=12000)
        inquiry=st.file_uploader('문의 파일에서 텍스트 가져오기',type=['txt','md','csv','docx','pdf','xlsx'],key='inquiry_file')
        if inquiry and st.button('파일 내용을 문의에 적용'):
            try:
                text=core.extract_file(inquiry.name,inquiry.getvalue())
                if len(text)>12000: raise ValueError('문의는 12,000자 이하로 나누어 주세요.')
                st.session_state.pending_question=text
                st.rerun()
            except Exception as exc:
                st.error(str(exc) if isinstance(exc,ValueError) else '파일을 읽지 못했습니다. 형식을 확인하세요.')
        evidence=core.search_evidence(question,eligible)
        st.caption(f"KMS 업무 기준 {sum(r['kind']=='KMS' for r in evidence)}개 · 이전 협의서 {sum(r['kind']=='협의서' for r in evidence)}개 · 검토 완료·사용 중인 자료에서 검색합니다.")
        for r in evidence:
            with st.expander(f"{r['ref']} · {r['title']}"):
                st.caption(f"{r['kind']} · 기준일 {r['effective']}")
                st.text(r['excerpt'])
        if any(r['title'].startswith('[가상 예시]') for r in evidence):
            st.warning('가상 예시 자료가 포함되어 있습니다. 실제 업무 답변으로 사용하지 마세요.')
        st.caption('초안 작성 버튼을 누르면 현재 문의와 위 근거가 OpenAI에 전송되며 API 비용이 발생합니다.')
        if st.button('근거로 답변 초안 작성',type='primary',width='stretch',disabled=not question.strip() or not evidence or not core.key()):
            with st.spinner('자료를 참고해 초안을 작성하고 있습니다…'):
                result=core.generate(question,evidence)
            if result['ok']:
                st.session_state.result=result
                st.session_state.generation+=1
                st.rerun()
            else: st.error(result['error'])
        if not core.key(): st.error('.env 또는 Streamlit Secrets에 OPENAI_API_KEY를 설정하세요.')
        if question.strip() and not evidence: st.info('관련 자료가 없습니다. KMS 탭에서 기준을 등록하거나 문의를 구체적으로 입력하세요.')
    with right:
        st.markdown('<div class="draft-heading">답변 초안</div>',unsafe_allow_html=True)
        result=st.session_state.get('result')
        if not result:
            st.info('문의와 관련 자료가 준비되면 왼쪽에서 초안을 작성하세요. 여기에서 근거를 확인하고 답변을 수정할 수 있습니다.')
        else:
            data=result['data']; version=st.session_state.generation
            if question!=result['question']: st.warning('문의가 변경되었습니다. 아래는 이전 문의의 초안입니다. 새 문의로 초안을 다시 작성하세요.')
            st.markdown('**문의 요약**'); st.write(data['summary'])
            if data['missing']: st.error('확답 전 필요한 정보: '+' / '.join(data['missing']))
            if data['checks']: st.warning('검토 사항: '+' / '.join(data['checks']))
            st.caption('AI가 작성한 초안입니다. 내용을 확인하고 이 영역에서 직접 수정한 뒤 저장하세요.')
            final=st.text_area('답변 초안',value=data['answer'],height=240,key=f'final_{version}',label_visibility='collapsed')
            with st.expander('답변에 사용된 근거',expanded=True):
                for r in result['evidence']:
                    if r['ref'] in data['source_ids']:
                        st.markdown(f"**{r['ref']} · {r['title']}**")
                        st.caption(f"기준일 {r['effective']} · {r['kind']}"); st.text(r['excerpt'])
            with st.form(f'review_{version}'):
                reviewer=st.text_input('검토자 이름')
                approved=st.checkbox('근거와 적용 조건을 확인했고 답변 검토를 완료했습니다.')
                st.caption('저장하면 협의서 검색에 추가됩니다. 검토 완료 자료만 AI 답변 근거로 사용합니다.')
                save=st.form_submit_button('협의서 저장',width='stretch')
                if save:
                    if question!=result['question']: st.error('문의가 변경되어 저장하지 않았습니다. 새 문의로 다시 작성하세요.')
                    else:
                        try:
                            hid=core.save_answer(result['question'],data['answer'],final,result,reviewer,approved)
                            prefix='[가상 예시] ' if any(r['title'].startswith('[가상 예시]') for r in result['evidence']) else ''
                            core.add_source(f'{prefix}협의서 #{hid}: {data["summary"][:60]}','협의서',f'질문: {result["question"]}\n답변: {final}',date.today(),approved)
                            st.success(f'답변 #{hid} 저장 완료 · '+('검토 완료' if approved else '검토 대기'))
                        except ValueError as exc: st.error(str(exc))
            st.download_button('현재 답변 TXT',final.encode('utf-8-sig'),file_name='answer_draft.txt',mime='text/plain',width='stretch')
            st.caption('AI 초안은 자동 발송하지 않습니다. 저장 시점의 문의·답변·근거를 저장 기록에 보관하고 협의서 검색에서 조회합니다.')

with tabs[2]:
    st.subheader('업무 지식 검색')
    query=st.text_input('KMS 업무 기준 검색',placeholder='예: 결제일 변경, 카드 분실')
    st.caption('등록된 KMS의 제목과 원문 전체를 검색합니다. 가상 예시·검토 전·사용 중지 자료도 조회할 수 있습니다. 여러 검색어는 모두 포함된 자료를 찾습니다.')
    if query.strip():
        found=core.search_catalog(query,core.sources())
        st.caption(f'검색 결과 {len(found)}개')
        if not found: st.info('제목과 원문에 일치하는 KMS 자료가 없습니다. 검색어를 줄이거나 띄어쓰기를 확인하세요.')
        for r in found:
            with st.expander(f"{r['title']} · #{r['id']}"):
                st.caption(f"기준일 {r['effective']} · {'검토 완료' if r['reviewed'] else '검토 전'} · {'사용 중' if r['active'] else '사용 중지'}")
                st.text(r['body'])
    st.subheader('자료 등록')
    st.caption('파일은 내용 미리보기 후 등록합니다. CSV·Excel은 행마다 별도 문서로 나누지 않고 한 자료로 등록합니다.')
    uploads=st.file_uploader('업무 자료 파일 여러 개',type=['txt','md','csv','xlsx','docx','pdf'],accept_multiple_files=True,key='source_files')
    prepared=[]
    for upload in uploads:
        try:
            body=core.extract_file(upload.name,upload.getvalue())
            prepared.append((upload.name,body))
            with st.expander(f'{upload.name} · 추출 내용 미리보기'):
                st.text(body[:6000]); st.caption(f'전체 {len(body):,}자. 미리보기는 처음 6,000자입니다.')
        except Exception as exc: st.error(f'{upload.name}: '+(str(exc) if isinstance(exc,ValueError) else '파일을 읽지 못했습니다. 형식을 확인하세요.'))
    with st.form('register_sources'):
        st.caption('이 영역에서는 KMS 업무 기준만 등록합니다.')
        effective=st.date_input('자료 기준일',value=date.today(),help='발행일 또는 업무 기준 적용일을 확인하세요.')
        title=st.text_input('직접 입력 자료 제목')
        body=st.text_area('직접 입력 내용',height=130,placeholder='업무 기준의 적용 대상, 한도, 신청 방법, 유의사항을 입력하세요.',max_chars=300000)
        reviewed=st.checkbox('등록 자료의 내용과 기준일을 검토했습니다.')
        submit=st.form_submit_button('자료 등록',type='primary',width='stretch')
        if submit:
            candidates=prepared+([(title,body)] if title.strip() or body.strip() else [])
            if not candidates: st.error('파일을 올리거나 제목과 내용을 입력하세요.')
            else:
                added=duplicates=0
                for name,text in candidates:
                    try:
                        if core.add_source(name,'KMS',text,effective,reviewed): added+=1
                        else: duplicates+=1
                    except ValueError as exc: st.error(str(exc))
                st.success(f'등록 {added}개 · 동일 내용 중복 {duplicates}개 제외')
                st.caption('등록한 자료는 아래 목록을 새로고침하면 표시됩니다.')
    if st.button('자료 목록 새로고침'): st.rerun()
    st.subheader('등록 자료 목록')
    current=[r for r in core.sources() if r['kind']=='KMS']
    if current:
        st.dataframe(pd.DataFrame([{'ID':r['id'],'제목':r['title'],'구분':r['kind'],'기준일':r['effective'],'검토 완료':bool(r['reviewed']),'사용 중':bool(r['active'])} for r in current]),hide_index=True,width='stretch')
        st.download_button('자료 전체 백업 CSV',core.export_csv(current),file_name='knowledge_backup.csv',mime='text/csv')
    else: st.info('등록된 자료가 없습니다. 파일 또는 직접 입력으로 시작하세요.')

with tabs[3]:
    st.subheader('이전 협의서 검색·조회')
    st.write('이전 고객 요청과 확인 내용, 현업 회신을 조회합니다. 개별 사례이므로 현재 KMS 기준과 적용 조건을 함께 확인하세요.')
    if st.button('협의서 새로고침'): st.rerun()
    cases=[r for r in core.sources() if r['kind']=='협의서']
    search_text=st.text_input('협의서 검색',placeholder='업무명, 고객 요청, 회신 내용, 협의서 번호')
    only_approved=st.checkbox('검토 완료·사용 중 협의서만 표시')
    cases=[r for r in cases if (not only_approved or (r['reviewed'] and r['active'])) and search_text.lower() in (r['title']+' '+r['body']).lower()]
    st.caption(f'이전 협의서 {len(cases)}개 · 가상 예시를 포함한 등록 자료를 조회합니다.')
    if cases:
        import hashlib
        selection_key='case_cells_'+hashlib.sha256(','.join(str(r['id']) for r in cases).encode()).hexdigest()[:16]
        selection=st.dataframe(pd.DataFrame([{'ID':r['id'],'협의서':r['title'],'작성일':r['effective'],'검토 상태':'검토 완료' if r['reviewed'] else '검토 전','사용 중':bool(r['active'])} for r in cases]),hide_index=True,width='stretch',key=selection_key,on_select='rerun',selection_mode='single-cell')
        selected=[selection.selection.cells[0][0]] if selection.selection.cells else []
        if selected and 0 <= selected[0] < len(cases):
            chosen=cases[selected[0]]
            st.markdown('**협의서 원문 · 고객 요청과 회신**')
            st.markdown(f"**{chosen['title']}**")
            if chosen['title'].startswith('[가상 예시]'): st.warning('체험용 가상 협의서입니다. 실제 회사 정책 또는 고객 처리 사례가 아닙니다.')
            st.caption(f"작성일 {chosen['effective']} · {'검토 완료' if chosen['reviewed'] else '검토 전'}")
            st.text(chosen['body'])
        else:
            st.info('위 협의서 목록에서 행을 클릭하면 원문과 고객 요청·회신이 표시됩니다.')
        st.download_button('검색된 협의서 CSV',core.export_csv(cases),file_name='previous_consultations.csv',mime='text/csv')
    else: st.info('검색 결과가 없습니다. 검색 조건을 바꾸거나 소개에서 가상 예시를 등록하세요. 작성한 답변은 협의서 저장으로 추가할 수 있습니다.')
