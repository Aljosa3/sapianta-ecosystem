from pathlib import Path
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,subprocess,tempfile
r=Path('/home/pisarna/work/sapianta-fl');e=r/'.github/governance/evidence'
rel='.github/governance/evidence/g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py';p=r/rel
s=importlib.util.spec_from_file_location('committed_bootstrap_same_r',p);f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
assert subprocess.check_output(['git','show','HEAD:'+rel],cwd=r)==p.read_bytes()
h=f.git(r,'rev-parse','HEAD');t=f.git(r,'rev-parse','HEAD^{tree}')
prior=e/'g77_256p11s2_wrong_scope_preparation_v1/live_binding/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.json';before=prior.read_bytes();c=json.loads(before)
proof=f.build_committed_review_transition(repository_root=r,context=c,current_admission_head=h,current_admission_tree=t)
with tempfile.TemporaryDirectory(prefix='p11_same_r_bootstrap_only_',dir=e) as scratch:
 output=Path(scratch)/'operation_state'
 result=f.derive_successor_bootstrap(repository_root=r,predecessor_context_path=prior,repository_head=h,repository_tree=t,operation_evidence_root=output)
 validated=f._validate_successor_bootstrap_assets(r,h,t,output)
 assert result==validated and not output.exists() and not (Path(scratch)/'live_binding').exists()
 sources=f._successor_bootstrap_sources(r,h,t)
 args=f.bootstrap_guest_command_arguments(sources['user-data'].decode(),'/mnt/dp-harness/G77_256FM_WRONG_ATTEMPT_VECTOR_ADAPTER_V1.py')
 assert args[0]==f.WRONG_SCOPE_ADMISSION_ADAPTER_SHA256 and args[2:4]==(h,t)
 assert c['guest_adapter_binding']['source_sha256']=='a59efdf4166fbc9c013a7ad7ddb23782d2fc7bc5873792960ec45b789e2df44c'
 assert prior.read_bytes()==before
 record={'schema_id':'P11_BOOTSTRAP_ROLE_SAME_R_V1','result':'SATISFIED','scope':'COMMITTED_SOURCE_BOOTSTRAP_ONLY_CERTIFICATION_FIXTURE','source_head':h,'source_tree':t,'validator':'FM.derive_successor_bootstrap','owner':'EXISTING_FM_BOOTSTRAP_CONTEXT_OWNER','source_sha256':f.sha256_path(p),'predecessor_file_sha256':f.sha256_path(prior),'predecessor_context_sha256':c['context_sha256'],'predecessor_adapter_sha256':c['guest_adapter_binding']['source_sha256'],'current_adapter_sha256':args[0],'lineage':proof,'native_bootstrap_validation':'PASS','source_member_sha256':{name:hashlib.sha256(raw).hexdigest() for name,raw in sources.items()},'user_data':sources['user-data'].decode(),'seed_sha256':result['seed_sha256'],'fixture_disposition':'REMOVED_AFTER_VALIDATION; NO_LIFECYCLE_OR_CONTEXT_CREATED','fresh_lifecycle_count_created':0,'operational_attempt_count':0,'human_operational_authority_count':0,'e05_credit':'12/18'}
assert not Path(scratch).exists()
Path('/tmp/p11_bootstrap_same_r_result.json').write_bytes(f.canonical_bytes(record))
print(json.dumps({k:v for k,v in record.items() if k not in ('lineage','user_data')},indent=2))
