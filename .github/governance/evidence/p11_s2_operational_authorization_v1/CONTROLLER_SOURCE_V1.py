import sys
sys.dont_write_bytecode=True
import pathlib,hashlib,json,subprocess,importlib.util,os
R=pathlib.Path('/home/pisarna/work/sapianta-fl')
D=R/'.github/governance/evidence/g77_256p11s2_wrong_scope_preparation_v1'
O=R/'.github/governance/evidence/p11_s2_operational_authorization_v1'
C=D/'live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json'
H='2649279b3aab63aee21b2b352c9aa569cbaa2e77';T='80e88a74895dd2711a0818bd0fa004ed1db071ee'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cb(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)+'\n').encode()
def git(*a):return subprocess.check_output(['git','-C',str(R),*a],text=True).strip()
def load(name,p):
 assert sha(p)==hashlib.sha256(subprocess.check_output(['git','-C',str(R),'show','HEAD:'+str(p.relative_to(R))])).hexdigest()
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
FM=load('s2_op_fm',R/'.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py')
LY=load('s2_op_ly',R/'.github/governance/evidence/g77_256ly_lt_parent_preauthority_readiness_v1/orchestration/G77_256LY_LT_PARENT_PREAUTHORITY_READINESS_V1.py')
LT=load('s2_op_lt',R/'.github/governance/evidence/g77_256lt_session_independent_one_shot_supervision_v1/harness/G77_256LT_SESSION_INDEPENDENT_ONE_SHOT_SUPERVISOR_V1.py')
def persist(n,v):
 p=O/n
 with p.open('xb') as f:f.write(cb(v));f.flush();os.fsync(f.fileno())
 fd=os.open(O,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
 return sha(p)
def seal(n,v):return persist(n,{'record':v,'record_sha256':hashlib.sha256(cb(v)).hexdigest()})
def check_seal(p):
 v=json.loads(p.read_bytes());assert hashlib.sha256(cb(v['record'])).hexdigest()==v['record_sha256'];return v['record']
def preserve():
 for p,h in check_seal(D/'ENTRY_V1.json')['preserved_sha256'].items():assert sha(pathlib.Path(p))==h,p
def identity():
 assert git('rev-parse','HEAD')==H and git('rev-parse','HEAD^{tree}')==T
 assert git('rev-parse','@{u}')==H and git('branch','--show-current')=='g77-256fl-wrong-attempt-preboot-blocker'
 assert not git('status','--porcelain','--untracked-files=no')
def reobserve():return LY.reobserve_before_authority_consumption(ltroot,leaf,ltready)
def final_admission():
 identity();preserve()
 env,ah=FM.load_authority(O/'FRESH_HUMAN_AUTHORITY_V1.json')
 return FM.validate_final_admission(repository_root=R,context=c,authority=env,authority_file_sha256=ah,supplied_authority_sha256=ah,observed_head=H,observed_tree=T,anchor_is_ancestor=FM.constitutional_anchor_is_ancestor(R),repository_clean=not git('status','--porcelain','--untracked-files=no'),observed_asset_sha256=FM.observe_context_assets(R,c),argv=c['canonical_argv'],canonical_argv_sha256=FM.load_canonicalizer(R).argv_sha256(c['canonical_argv']),receipt_namespace_consumed=any(p.exists() for p in FM.receipt_consumable_paths(R,c)),candidate_source_path=pathlib.Path(FM.CANDIDATE),committed_review_transitions=[pr])
assert not O.exists(), 'S2 operational record already exists; no repeat'
identity();preserve()
qpath=D/'HUMAN_DECISION_REQUEST_V1.json'
assert sha(qpath)=='58bd1abcb53be63a12cd6be6da8e6423f250eaf8e05685102972cc65c541cf86'
q=check_seal(qpath)
assert q['human_decision_state']=='PENDING' and q['operational_attempt_limit']==1 and q['retry_limit']==q['repair_limit']==q['replay_limit']==0
c=FM.fresh_context.load_context(C,repository_root=R)
assert q['subject_context_sha256']==c['context_sha256']=='d5b37da575af8407efbfefef6c22d8ba644ef23f6dc108b9b43d181e20140aa1'
assert q['subject_file_sha256']==sha(C) and q['operation_identity']==c['operation_identity']
assert q['current_admission_head']==H and q['current_admission_tree']==T
assert q['authorized_scope']=='P11_DA_ONE_BOUNDED_OPERATIONAL_ATTEMPT_V1' and q['presented_scope']=='P11_DA_DIFFERENT_OPERATIONAL_SCOPE_V1'
ltready=json.loads((D/'LT_PARENT_READINESS_V1.json').read_bytes());lo=ltready['observation']
ltroot=pathlib.Path(lo['permitted_generation_root']);leaf=pathlib.Path(lo['lt_lifecycle_leaf'])
assert sha(D/'LT_PARENT_READINESS_V1.json')==q['lt_parent_readiness_sha256']
assert not leaf.exists()
O.mkdir(mode=0o700)
stage='PREAUTHORITY_READINESS';created=0;consumed=0;launched=False
try:
 (O/'CONTROLLER_SOURCE_V1.py').write_bytes(pathlib.Path(__file__).read_bytes())
 source={'source':'CURRENT_USER_MESSAGE','text':'YES','answers':'Immediately preceding exact S2 Human operational decision presentation','request_file_sha256':sha(qpath),'subject_context_sha256':c['context_sha256'],'operation_identity':c['operation_identity'],'current_admission_head':H,'current_admission_tree':T,'human_decision_question':q['human_decision_question'],'scope_restrictions':'Exactly one attempt; no S1 reuse, retry, replay, repair, new lifecycle, network/provider access or unrelated effects; all native final checks required','revocation_or_supersession_received_in_current_conversation':False}
 source_sha=persist('HUMAN_DECISION_SOURCE_V1.json',source)
 pr=FM.build_committed_review_transition(repository_root=R,context=c,current_admission_head=H,current_admission_tree=T)
 assert pr['transition_sha256']==q['committed_review_transition_sha256']
 persist('COMMITTED_REVIEW_TRANSITION_V1.json',pr)
 static=FM.authority_free_static_readiness(repository_root=R,context=c,observed_head=H,observed_tree=T,repository_clean=not git('status','--porcelain','--untracked-files=no'),observed_asset_sha256=FM.observe_context_assets(R,c),committed_review_transitions=[pr])
 receipt=FM.validate_receipt_parent_ready(R,c)
 ly=reobserve()
 seal('APPROVAL_TIME_READINESS_V1.json',dict(fm=static,receipt=receipt,ly=ly,source_sha256=source_sha,authority_created_count=0,operation_attempt_count=0))
 stage='AUTHORITY_CREATION'
 authorization={'schema_id':FM.AUTHORIZATION_SCHEMA,'authorization_present':True,'authorization_kind':'FRESH_HUMAN_OPERATIONAL_AUTHORIZATION','authorization_source_sha256':source_sha,'authorized_context_sha256':c['context_sha256'],'authorized_operation_identity':c['operation_identity'],'authorized_generation_identity':c['generation_identity'],'authorized_vector':'WRONG_SCOPE','authorized_repository_head':H,'authorized_repository_tree':T,'authorized_constitutional_anchor_head':FM.CONSTITUTIONAL_ANCHOR_HEAD,'authorized_candidate_sha256':c['candidate_manifest_sha256'],'authorized_canonical_argv_sha256':c['canonical_argv_sha256'],'authorized_wrapper_sha256':c['wrapper_fc_er_che_schema_hashes']['wrapper'],'authorized_fk_adapter_sha256':FM.FK_ADAPTER_SHA256,'vm_boot_limit':1,'qemu_system_execution_limit':1,'wrong_scope_operational_attempt_limit':1,'retry_limit':0,'repair_limit':0,'replay_limit':0,'receipt_namespace_must_be_unconsumed':True,'network_authorized':False,'provider_authorized':False,'trusted_access_authorized':False,'authorization_reusable':False,'auto_continuable':False}
 a=FM.write_authority_handoff(O/'FRESH_HUMAN_AUTHORITY_V1.json',authorization);created=1
 stage='FINAL_AUTHORITY_AND_INVOCATION_BINDING'
 admission=final_admission()
 base=FM.build_preconsumption_invocation_binding(repository_root=R,operation_context=C,live_candidate_binding=R/FM.CANDIDATE,execution_authority=O/'FRESH_HUMAN_AUTHORITY_V1.json')
 validated=FM.validate_preconsumption_invocation_binding(repository_root=R,operation_context=C,live_candidate_binding=R/FM.CANDIDATE,execution_authority=O/'FRESH_HUMAN_AUTHORITY_V1.json',envelope=base)
 argv=validated['final_fm_argv']+['--committed-review-transition',str((O/'COMMITTED_REVIEW_TRANSITION_V1.json').relative_to(R)),'--committed-review-transition-sha256',sha(O/'COMMITTED_REVIEW_TRANSITION_V1.json')]
 binding={'fm_owned_base_binding':base,'final_fm_argv':argv,'final_fm_argv_sha256':hashlib.sha256(cb(argv)).hexdigest(),'transition_sha256':pr['transition_sha256'],'transition_file_sha256':sha(O/'COMMITTED_REVIEW_TRANSITION_V1.json'),'binding_is_authority':False,'operational_attempt_count':0}
 bs=seal('FM_INVOCATION_BINDING_V1.json',binding)
 lt=LT.build_binding(lifecycle_id='G77_256P11S2_WRONG_SCOPE_LIFECYCLE_001',invocation_id='G77_256P11S2_WRONG_SCOPE_INVOCATION_001',invocation_binding_identity='FM_BINDING_SHA256:'+bs,fm_input_identity='CONTEXT_FILE_SHA256:'+sha(C),admission_identity='HEAD:'+H+'__TREE:'+T,authority_binding_sha256=a['authority_file_sha256'],execution_class='FUTURE_SEPARATELY_AUTHORIZED_FM_INVOCATION',working_directory=R,argv=argv)
 LT.write_binding_once(O/'LT_INVOCATION_BINDING_V1.json',lt);LT.load_binding(O/'LT_INVOCATION_BINDING_V1.json')
 seal('FINAL_PRECONSUMPTION_V1.json',dict(authority=a,admission=admission,authority_state='GRANTED_UNCONSUMED',created_count=1,consumed_count=0,operational_attempt_count=0,lt_binding_sha256=sha(O/'LT_INVOCATION_BINDING_V1.json'),revocation_or_supersession_in_current_conversation=False,guest_authority_checks='REQUIRED_IN_GUEST; NOT_YET_OBSERVED'))
 stage='FINAL_LY_PRECONSUMPTION_REOBSERVATION'
 final_admission()
 assert FM.load_committed_review_transition(O/'COMMITTED_REVIEW_TRANSITION_V1.json',sha(O/'COMMITTED_REVIEW_TRANSITION_V1.json'))==pr
 assert check_seal(O/'FM_INVOCATION_BINDING_V1.json')==binding
 assert json.loads((O/'LT_INVOCATION_BINDING_V1.json').read_bytes())==lt
 final_ly=reobserve()
 seal('LY_PRECONSUMPTION_REOBSERVATION_V1.json',final_ly)
 stage='AUTHORITY_CONSUMPTION'
 assert not leaf.exists() and not (O/'AUTHORITY_CONSUMPTION_V1.json').exists()
 seal('AUTHORITY_CONSUMPTION_V1.json',dict(authority_file_sha256=a['authority_file_sha256'],source_sha256=source_sha,authority_state_before='GRANTED_UNCONSUMED',authority_state_after='CONSUMED__NONREUSABLE',authority_created_count=1,authority_consumed_count=1,authority_reusable=False,operational_attempt_count_at_consumption=0,retry_count=0));consumed=1
 stage='LT_ONE_SHOT_LAUNCH'
 handoff=LT.launch_detached(leaf,O/'LT_INVOCATION_BINDING_V1.json');launched=True
 seal('LT_LAUNCH_HANDOFF_V1.json',dict(handoff=handoff,authority_consumed_count=1,retry_count=0,lt_state=str(leaf)))
 print(json.dumps({'result':'ONE_SHOT_HANDED_TO_LT','handoff':handoff,'authority_created':created,'authority_consumed':consumed,'lt_state':str(leaf)}))
except BaseException as exc:
 seal('FAIL_CLOSED_STOP_V1.json',dict(stage=stage,error=type(exc).__name__+': '+str(exc),authority_created_count=created,authority_file_present=(O/'FRESH_HUMAN_AUTHORITY_V1.json').exists(),authority_consumed_count=consumed,lt_handoff_completed=launched,lt_state_exists=leaf.exists(),pre_receipt_exists=pathlib.Path(c['pre_receipt_path']).exists(),post_receipt_exists=pathlib.Path(c['post_receipt_path']).exists(),e05_credit='12/18',retry_authorized=False,repair_authorized=False,authority_reusable=False))
 print(json.dumps({'result':'FAIL_CLOSED_STOP','stage':stage,'error':str(exc),'authority_created':created,'authority_consumed':consumed,'lt_state_exists':leaf.exists()}))
 raise
