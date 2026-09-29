import sys
sys.dont_write_bytecode=True
import pathlib,json,hashlib,importlib.util,subprocess
R=pathlib.Path('/home/pisarna/work/sapianta-fl');D=R/'.github/governance/evidence/g77_256p11s3_wrong_scope_preparation_v1';O=R/'.github/governance/evidence/p11_s3_operational_authorization_v1'
def cb(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)+'\n').encode()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def inner(p):
 v=read(p);assert hashlib.sha256(cb(v['record'])).hexdigest()==v['record_sha256'];return v['record']
def write(n,v):
 with (O/n).open('xb') as f:f.write(cb(v))
def load(n,p):
 assert sha(p)==hashlib.sha256(subprocess.check_output(['git','-C',str(R),'show','HEAD:'+str(p.relative_to(R))])).hexdigest()
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
lt=load('s3_terminal_lt',R/'.github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py')
fm=load('s3_terminal_fm',R/'.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py')
c=fm.fresh_context.load_context(D/'live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json',repository_root=R)
state=pathlib.Path(read(D/'LT_PARENT_READINESS_V1.json')['observation']['lt_lifecycle_leaf'])
events=lt.read_journal(state);last=events[-1]['event']
assert [e['event']['state'] for e in events]==['NOT_STARTED','STARTED','RUNNING','TERMINATED_WITH_STATUS']
assert last['details']['process_exit_status']==0 and last['details']['launch_attempt_count']==1
_,bs,bfs=lt.load_binding(O/'LT_INVOCATION_BINDING_V1.json')
assert all(e['event']['binding_file_sha256']==bfs and e['event']['binding_sha256']==bs for e in events)
pre=read(pathlib.Path(c['pre_receipt_path']));post=read(pathlib.Path(c['post_receipt_path']))
authority,ah=fm.load_authority(O/'FRESH_HUMAN_AUTHORITY_V1.json')
source=read(O/'HUMAN_DECISION_SOURCE_V1.json');assert source['text']=='YES'
assert authority['authorization']['authorization_source_sha256']==sha(O/'HUMAN_DECISION_SOURCE_V1.json')
for receipt in [pre,post]:
 assert receipt['context_sha256']==c['context_sha256'] and receipt['operation_identity']==c['operation_identity']
 assert receipt['execution_authority_file_sha256']==ah and receipt['vector']['argv']==c['canonical_argv']
 assert receipt['vector']['canonical_argv_sha256']==fm.load_canonicalizer(R).argv_sha256(c['canonical_argv'])
 assert receipt['execution_attempt_count']==1 and receipt['automatic_retry_count']==0
assert post['process_exit_status']==0 and pre['started_unix_ns']==post['started_unix_ns']
assert inner(O/'AUTHORITY_CONSUMPTION_V1.json')['authority_state_after']=='CONSUMED__NONREUSABLE'
assert inner(O/'LY_PRECONSUMPTION_REOBSERVATION_V1.json')['result']=='VERIFIED__SAME_PREPARED_PARENT_OBJECT__SAME_INTENDED_LT_LEAF__LEAF_ABSENT'
serial=pathlib.Path(c['serial_path']);text=serial.read_text(errors='replace')
assert text.count('G77_256FM_BOOT_MARKER=PASS')==1 and text.count('G77_256FM_HARNESS_EXIT_STATUS=40')==1 and 'reboot: Power down' in text
runtime=pathlib.Path(c['runtime_export_root']);raw=runtime/'G77_256P11S3_RAW_EXECUTION_EVIDENCE_V1.jsonl'
records=[json.loads(l) for l in raw.read_text().splitlines()]
assert [r['record_sequence'] for r in records]==list(range(7))
assert [r['record_type'] for r in records]==['execution_context','commissioning_P01','commissioning_P02','commissioning_P03','commissioning_P04','first_failure','guest_teardown']
assert all(r['facts']['result']=='PASS' for r in records[1:5])
failure=records[5]['facts'];error="ModuleNotFoundError: No module named 'sapianta_system'"
assert failure['first_failure']==error
td=read(runtime/'G77_256P11S3_GUEST_TEARDOWN_SEAL_V1.json')
assert td['first_failure']==error and td['teardown_state']=='COMPLETE'
assert td['raw_record_count']==len(records) and td['raw_evidence_sha256']==sha(raw)
assert records[6]['facts']['fixture_root_absent'] is True
assert td['execution_counters']==failure['execution_counters']==records[6]['facts']['execution_counters']
counters=td['execution_counters']
assert counters['vm_boot_count']==counters['vm_creation_count']==1
assert all(v==0 for k,v in counters.items() if k not in ['vm_boot_count','vm_creation_count'])
manifest=read(runtime/'G77_256P11S3_CONTINUATION_MANIFEST_TERMINAL_V1.json')
assert hashlib.sha256(cb(manifest['manifest'])).hexdigest()==manifest['manifest_sha256']
assert manifest['manifest']['first_failure_or_current_result'].endswith(error)
assert manifest['manifest']['authority_state']['authority_survives'] is False
assert not (runtime/'G77_256P11S3_GUEST_EXECUTION_SEAL_V1.json').exists()
for p,h in inner(D/'ENTRY_V1.json')['preserved_sha256'].items():assert sha(R/p)==h,p
assert sha(D/'live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json')==source['subject_file_sha256']
assert not lt.process_identity_is_live(last['details']['child_identity'])
qemu=[]
for p in pathlib.Path('/proc').iterdir():
 if p.name.isdigit():
  try:argv=(p/'cmdline').read_bytes().split(b'\0')
  except (FileNotFoundError,PermissionError,ProcessLookupError):continue
  if argv and argv[0].endswith(b'qemu-system-x86_64') and any(c['overlay_path'].encode() in a for a in argv):qemu.append(int(p.name))
assert not qemu
archive=O/'terminal_evidence';archive.mkdir()
paths=[serial,pathlib.Path(c['pre_receipt_path']),pathlib.Path(c['post_receipt_path']),*sorted(state.glob('*.json')),state/'supervisor.log',state/'child.log',*sorted(runtime.glob('*'))]
for p in paths:
 if p.is_file():
  target=archive/('SERIAL_CONSOLE_V1.log' if p==serial else p.name)
  with target.open('xb') as f:f.write(p.read_bytes())
  assert sha(target)==sha(p)
result={
 'SELECTED_RESULT':'P11_WRONG_SCOPE_S3_OPERATIONAL_ATTEMPT_FAIL_CLOSED_AT_P05_IMPORT',
 'HUMAN_DECISION':'YES; exact S3 request authenticated','HUMAN_DECISION_REQUEST_SHA256':sha(O/'HUMAN_DECISION_REQUEST_V1.json'),
 'S3_SUBJECT_IDENTITY':c['context_sha256'],'OPERATION_IDENTITY':c['operation_identity'],
 'HUMAN_ACT_CREATED_COUNT':1,'HUMAN_ACT_CONSUMED_COUNT':1,'HUMAN_ACT_REPLAY_COUNT':0,
 'AUTHORITY_STATE':'CONSUMED__NONREUSABLE','OPERATIONAL_ATTEMPT_AUTHORIZED':'YES_FOR_COMPLETED_SINGLE_ATTEMPT_ONLY',
 'OPERATIONAL_ATTEMPT_EXECUTED':'YES','OPERATIONAL_ATTEMPT_COUNT':1,'LT_CHILD_LAUNCH_COUNT':1,'VM_BOOT_COUNT':1,
 'FM_PROCESS_EXIT_STATUS':0,'QEMU_PROCESS_EXIT_STATUS':0,'GUEST_HARNESS_EXIT_STATUS':40,'LT_TERMINAL_STATE':'TERMINATED_WITH_STATUS',
 'RETRY_COUNT':0,'REPLAY_COUNT':0,'REPAIR_COUNT':0,'AUTO_CONTINUABLE':False,
 'GUEST_AUTHORITY_CREATED_COUNT':0,'GUEST_P11_ENTRY_COUNT':0,'GUEST_P11_INVOCATION_COUNT':0,'GUEST_E05_CASE_EXECUTION_COUNT':0,
 'GUEST_COUNTERS':counters,'GUEST_COMMISSIONING_OBSERVED_PASS':['P01','P02','P03','P04'],
 'COUNTER_INTERPRETATION':'One host-supervised attempt/VM boot; zero guest E05 case execution. P01-P04 per-record PASS; aggregate P01-P12 counters remain emitted zeros, not rewritten.',
 'FAILURE_CLASS':'GUEST_P05_DEPENDENCY_IMPORT_FAILURE','NATIVE_ERROR':error,
 'FAILURE_NOVELTY':'New observed guest dependency-import edge after corrected runtime identity gate and P01-P04; not the closed ER/bootstrap identity failure',
 'CURRENT_NATIVE_EDGE':'commissioning P04 -> P05 custody-process import',
 'MANDATORY_REQUIREMENT_R':'Guest P05 must import its existing custody-process dependencies before live role-bound SO_PEERCRED validation',
 'REQUIREMENT_OWNER':'Existing ER commissioning P05 / custody-process dependency surface',
 'REQUIREMENT_VALIDATOR':'Native ER.main P05 import and commissioning evidence',
 'CURRENT_REQUIREMENT_RESULT':'UNSATISFIED; ModuleNotFoundError',
 'MINIMUM_GAP_CLASSIFICATION':'GUEST_RUNTIME_DEPENDENCY_AVAILABILITY; root cause not established',
 'CRITICAL_PATH_DEPENDENCY_GATE':'MANDATORY P05 prerequisite; no repair or new execution authorized',
 'LAST_VERIFIED_WORKING_EDGE':'Guest current identity authentication and P01-P04; terminal guest teardown subsequently complete',
 'FIRST_NON_COMPLETE_WORKING_EDGE':'P05 custody-process dependency import',
 'SCOPE_COMPARATOR_REACHED':'NO','WRONG_SCOPE_ACCEPTANCE':'NOT_ESTABLISHED',
 'GUEST_TEARDOWN':'COMPLETE; fixture root absent; raw evidence hash verified',
 'VM_SHUTDOWN':'POWER_DOWN observed; QEMU/FM returned; no matching QEMU or live supervised child',
 'HOST_TRANSIENT_STATE':'RETAINED_SPENT_EVIDENCE; no reset or reuse',
 'S2_PRESERVED':'YES','S2_AUTHORITY_REUSED':'NO','S3_SEALED_SUBJECT_PRESERVED':'YES',
 'ER_CORRECTION_PRESERVED':'YES; passed guest identity authentication','BOOTSTRAP_ROLE_CORRECTION_PRESERVED':'YES',
 'E05_STATE':'PARTIAL','E05_FRONTIER':'WRONG_SCOPE','E05_CREDIT':'12/18','E05_CREDIT_DELTA':0,
 'MINIMUM_MISSING_CAPABILITY':'NONE_ESTABLISHED','MINIMUM_MISSING_BINDING':'Exact cause of unavailable guest sapianta_system dependency unresolved',
 'MINIMUM_MISSING_PROOF':'Authenticated operational WRONG_SCOPE denial acceptance',
 'MINIMUM_LEGAL_NEXT_DELTA':'Bounded review of terminal P05 dependency-import failure; any repair or fresh lifecycle requires separate authority',
 'AIGOL_CODE_PROGRESS':'NO','AIGOL_CAPABILITY_PROGRESS':'NO','TASK_EXECUTION_PROGRESS_THROUGH_AIGOL':'YES',
 'AIGOL_NATIVE_FRONTIER_ADVANCED':'YES_TO_P05_DEPENDENCY_BOUNDARY; no acceptance credit',
 'AIGOL_PROBLEM_LOCALIZATION_PROGRESS':'YES','AIGOL_SEMANTIC_OPERATIONALIZATION_PROGRESS':'YES; exact S3 authority exercised once and corrected identity semantics passed in guest',
 'AIGOL_PROGRESS_AREA':'S3_ONE_SHOT_OPERATIONAL_COMMISSIONING','AIGOL_NEXT_BLOCKER':'P05 guest dependency import; no repair authorization',
 'TRUE_BOUNDARY_REACHED':'YES','TRUE_BOUNDARY_CLASS':'TERMINAL_FAIL_CLOSED_OUTCOME__NO_RETRY_OR_REPAIR',
 'EXECUTION_CHECKPOINT':{'HEAD':source['current_admission_head'],'TREE':source['current_admission_tree']},
 'RECOVERY_REFERENCES':{'evidence_root':str(O),'subject':str(D/'live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'),'lt_state':str(state),'transient_root':c['transient_root']},
 'FINAL_HANDOFF_CONSISTENCY':'PASS; host attempt and guest non-entry counters distinguished',
 'PROPOSED_SUCCESSOR':'P11_WRONG_SCOPE_S3_P05_DEPENDENCY_IMPORT_FAILURE_BOUNDED_REVIEW'
}
write('TERMINAL_REDUCTION_V1.json',{'record':result,'record_sha256':hashlib.sha256(cb(result)).hexdigest()})
with (O/'TERMINAL_REPORT_V1.md').open('x') as f:
 f.write('# S3 one-shot terminal outcome\n\nThe single Human-authorized S3 attempt failed closed before WRONG_SCOPE acceptance. E05 remains PARTIAL / WRONG_SCOPE / 12/18, delta 0.\n\nFinal host admission and LY checks passed. One fresh host authority was created and consumed, one LT child and VM boot occurred, and FM/QEMU returned 0 after guest poweroff. Guest harness status was 40: ModuleNotFoundError: No module named sapianta_system. Host exit 0 is not guest acceptance.\n\nGuest current identity authentication and individual commissioning P01-P04 passed. The next ER step imports custody-process dependencies for P05; no P05 result or scope comparator result was emitted. The guest reports zero authority creation, P11 entry/invocation and E05 case execution. These differ from the single host-supervised attempt. Aggregate P01-P12 counters remain their emitted zeros. No counters were synthesized.\n\nSeven raw records and the teardown seal authenticate complete guest teardown and fixture absence. The final manifest reports no surviving guest authority. Host authority is consumed/nonreusable. No matching QEMU process or live LT child remains; spent checkout/overlay state is retained as evidence without reset. S2 and the sealed S3 subject are unchanged.\n\nThe failure is localized to the P04-to-P05 dependency-import edge; the underlying availability cause has not been established. Both prior corrections remain closed. No source mutation, repair, retry, replay or additional lifecycle occurred. Next boundary: separate bounded terminal-failure review, with no further operation authorized.\n')
with (O/'TERMINAL_REDUCER_SOURCE_V1.py').open('xb') as f:f.write(pathlib.Path(__file__).read_bytes())
write('TERMINAL_ARTIFACT_BINDINGS_V1.json',{str(p.relative_to(R)):sha(p) for p in sorted(O.rglob('*')) if p.is_file()})
print(json.dumps({k:result[k] for k in ['SELECTED_RESULT','OPERATIONAL_ATTEMPT_COUNT','GUEST_HARNESS_EXIT_STATUS','E05_CREDIT','S2_PRESERVED','FINAL_HANDOFF_CONSISTENCY']}))
