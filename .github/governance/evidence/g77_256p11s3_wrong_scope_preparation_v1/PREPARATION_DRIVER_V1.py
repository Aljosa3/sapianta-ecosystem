import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, subprocess, traceback
from pathlib import Path
R=Path('/home/pisarna/work/sapianta-fl')
D=R/'.github/governance/evidence/g77_256p11s3_wrong_scope_preparation_v1'
P=D/'live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
T=Path('/tmp/g77_256p11s3_wrong_scope_20260929')
S2=R/'.github/governance/evidence/g77_256p11s2_wrong_scope_preparation_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
SESSION=Path('/home/pisarna/.codex/sessions/2026/09/29/rollout-2026-09-29T08-40-30-01a0ebe4-ba10-7930-82e6-57342b0e41d8.jsonl')
ENTRY='2225db682446d1742fa55f6d2e0e96d95f3f1844'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); sys.modules[name]=m; s.loader.exec_module(m); return m
FM=load('s3_fm',R/'.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git','-C',str(R),*args],text=True).strip()
def write(name,value):
 with (D/name).open('xb') as f: f.write(FM.canonical_bytes(value))
def record(name,value): write(name,dict(record=value,record_sha256=hashlib.sha256(FM.canonical_bytes(value)).hexdigest()))
def preserve():
 for p,h in json.loads((D/'ENTRY_V1.json').read_text())['record']['preserved_sha256'].items(): assert sha(R/p)==h,p
 return True
def context(): return FM.fresh_context.load_context(P,repository_root=R)
def proof(c): return FM.build_committed_review_transition(repository_root=R,context=c,current_admission_head=git('rev-parse','HEAD'),current_admission_tree=git('rev-parse','HEAD^{tree}'))
phase=sys.argv[1]
try:
 if phase=='create':
  assert git('rev-parse','HEAD')==ENTRY
  assert not git('status','--porcelain','--untracked-files=no')
  assert not D.exists() and not T.exists()
  lines=SESSION.read_text().splitlines()
  question=json.loads(lines[321]); decision=json.loads(lines[328])
  assert question['payload']['role']=='assistant' and decision['payload']['role']=='user'
  qt='\n'.join(x.get('text','') for x in question['payload']['content'])
  dt='\n'.join(x.get('text','') for x in decision['payload']['content'])
  assert 'exactly one new, distinct P11/E05 WRONG_SCOPE lifecycle' in qt and dt.rstrip().endswith('YES')
  preserved=json.loads((R/'.github/governance/evidence/p11_s2_operational_authorization_v1/TERMINAL_ARTIFACT_BINDINGS_V1.json').read_text())
  for p,h in preserved.items(): assert sha(R/p)==h,p
  for root in [S2.parent.parent,R/'.github/governance/evidence/p11_s2_operational_authorization_v1']:
   for p in root.rglob('*'):
    if p.is_file(): preserved[str(p.relative_to(R))]=sha(p)
  native={str(Path(m.__file__).relative_to(R)):sha(Path(m.__file__)) for m in [FM,FM.fresh_context]}
  for p,h in native.items(): assert hashlib.sha256(subprocess.check_output(['git','-C',str(R),'show','HEAD:'+p])).hexdigest()==h
  D.mkdir(mode=0o700)
  record('ENTRY_V1.json',dict(head=ENTRY,tree=git('rev-parse','HEAD^{tree}'),branch=git('branch','--show-current'),tracking=git('rev-parse','@{u}'),live_remote=ENTRY,preserved_sha256=preserved,native_committed_sha256=native,entry_status=git('status','--porcelain')))
  record('PREPARATION_PERMISSION_V1.json',dict(status='APPLICABLE',source_session=str(SESSION),question_line=322,decision_line=329,question=qt,human_response=dt,question_record_sha256=hashlib.sha256(lines[321].encode()).hexdigest(),decision_record_sha256=hashlib.sha256(lines[328].encode()).hexdigest(),owner='P11_CONSUMER_CONSTITUTIONAL_OWNER / HUMAN_CONSTITUTIONAL_AUTHORITY',contracts=['docs/governance/G77_256BW_EXACT_HUMAN_P11_OUTCOME_CAUSALITY_AND_ABSTRACT_CONSTITUTIONAL_OWNER_DECISION_RESPONSE_V1.md','docs/governance/G77_256BY_EXACT_HUMAN_P11_CALLER_BOUNDED_LIFECYCLE_AND_DISPOSAL_RETENTION_DECISION_RESPONSE_V1.md'],reason='Exact YES grants one fresh preparation through full native readiness on corrected canonical route; no fixed commit pin or implementation-expiry term. No lifecycle instantiated by prior failure; subsequent correction request explicitly retains grant and forbids creation. Current resumption preserves scope/cardinality. BY nonreuse and separate operational authorization preserved.',authorized_fresh_lifecycle_count=1,previous_created_count=0,operational_authority=False))
  write('PRIOR_NATIVE_BLOCKER_V1.json',json.loads(Path('/tmp/p11_fresh_preparation_native_blocker.json').read_text()))
  (D/'RESUMPTION_REQUEST_V1.txt').write_bytes(Path('/home/pisarna/.codex/attachments/d2cd5dc7-8b70-4c33-9f71-c95e9998b04b/pasted-text.txt').read_bytes())
  c=FM.build_operation_context(repository_root=R,repository_head=ENTRY,repository_tree=git('rev-parse','HEAD^{tree}'),generation_identity='G77_256P11S3_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1',operation_identity='G77_256P11S3_E05_WRONG_SCOPE_PREPARATION_001',identity_namespace_prefix='G77_256P11S3',operation_evidence_root=D/'operation_state',transient_root=T,predecessor_context_path=S2)
  old=json.loads(S2.read_text())
  for k in ['operation_identity','context_sha256','operation_evidence_root','transient_root','receipt_parent']: assert c[k]!=old[k]
  FM.validate_immutable_context_bindings(R,c)
  fresh=FM.fresh_context.validate_freshness(c)
  P.parent.mkdir(); write(str(P.relative_to(D)),c)
  record('SUBJECT_VALIDATION_V1.json',dict(context_sha256=c['context_sha256'],subject_file_sha256=sha(P),fresh_context_validation='PASS',fresh_subject_validation='PASS',freshness=fresh,fresh_lifecycle_count_created=1,s2_preserved=preserve(),operational_attempt_count=0,human_operational_authority_created_count=0))
  print(json.dumps(dict(phase=phase,result='PASS',context_sha256=c['context_sha256'])))
 elif phase=='review':
  c=context(); preserve()
  assert subprocess.check_output(['git','-C',str(R),'show','HEAD:'+str(P.relative_to(R))])==P.read_bytes()
  record('REVIEW_INTRODUCTION_V1.json',dict(review_head=git('rev-parse','HEAD'),review_tree=git('rev-parse','HEAD^{tree}'),subject_sha256=sha(P),context_sha256=c['context_sha256'],next_edge='CANONICAL_COMMITTED_REVIEW_TO_CURRENT_ADMISSION',is_authority=False))
  record('ADMISSION_DEPENDENCY_CLASSIFICATION_V1.json',dict(current_native_edge='committed review to current admission',mandatory_requirement_r='Nonempty exact committed delta after immutable review introduction',requirement_owner='FM committed review/admission owner',requirement_validator='build_committed_review_transition / _exact_committed_delta',current_requirement_result='UNSATISFIED_AT_REVIEW_INTRODUCTION',minimum_gap_classification='ORDINARY_DERIVED_PROOF_EDGE',failure_novelty='Existing additive admission lifecycle; omitted review-introduction evidence step, no source defect',critical_path_dependency_gate='MANDATORY for exact subject admission',nrdrl='Record committed review introduction and additive admission evidence, then recompute same native transition',new_capability_required=False,new_source_mutation_required=False,new_authority_required=False,automatic_operational_retry_count=0))
  print('PASS: immutable review introduction recorded; additive evidence ready')
 elif phase=='materialize':
  c=context(); preserve(); pr=proof(c)
  assert not git('status','--porcelain','--untracked-files=no')
  admission=FM.authenticate_review_to_current_admission(repository_root=R,context=c,observed_head=git('rev-parse','HEAD'),observed_tree=git('rev-parse','HEAD^{tree}'),committed_review_transitions=[pr])
  base=c['qemu_executable_base_seed_checkout_bindings']['base']; assert sha(Path(base['path']))==base['sha256']
  record('ADMISSION_V1.json',dict(proof=pr,admission=admission,base_sha256=base['sha256']))
  result=FM.materialize_operation_state(repository_root=R,context=c,context_source_path=P,committed_review_transitions=[pr])
  receipts=FM.prepare_receipt_parent(R,c)
  record('MATERIALIZATION_V1.json',dict(materialization=result,receipt_readiness=receipts,s2_preserved=preserve(),operational_attempt_count=0))
  print('PASS: fresh materialization and receipt parent; no QEMU execution')
 elif phase in ['readiness','endpoint']:
  c=context(); preserve(); pr=proof(c)
  clean=not git('status','--porcelain','--untracked-files=no'); assert clean
  result=FM.authority_free_static_readiness(repository_root=R,context=c,observed_head=git('rev-parse','HEAD'),observed_tree=git('rev-parse','HEAD^{tree}'),repository_clean=clean,observed_asset_sha256=FM.observe_context_assets(R,c),committed_review_transitions=[pr])
  LY=load('s3_ly',R/'.github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/orchestration/G77_256LY_LT_PARENT_PREAUTHORITY_READINESS_V1.py')
  ltroot=D/'lt_preparation'; leaf=ltroot/'lt_supervision/G77_256P11S3_WRONG_SCOPE_OPERATION_001'
  if phase=='readiness':
   ltroot.mkdir(mode=0o700); lt=LY.prepare_lt_parent_readiness(ltroot,leaf); write('LT_PARENT_READINESS_V1.json',lt)
  else: lt=json.loads((D/'LT_PARENT_READINESS_V1.json').read_text())
  observed=LY.reobserve_before_authority_consumption(ltroot,leaf,lt)
  record('READINESS_V1.json' if phase=='readiness' else 'FINAL_ENDPOINT_VALIDATION_V1.json',dict(head=git('rev-parse','HEAD'),tree=git('rev-parse','HEAD^{tree}'),preflight=result,lt_reobservation=observed,transition=pr,s2_preserved=preserve(),operational_attempt_count=0,human_operational_authority_created_count=0,e05_credit='12/18'))
  print('PASS: full native authority-free static readiness and LY reobservation')
 else: raise ValueError(phase)
except Exception as exc:
 failure=dict(phase=phase,type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc(),subject_created=P.exists(),runtime_root_exists=(D/'operation_state').exists(),transient_root_exists=T.exists(),operational_attempt_count=0)
 if D.exists(): record('FAILURE_'+phase.upper()+'_V1.json',failure)
 print(json.dumps(failure)); raise
