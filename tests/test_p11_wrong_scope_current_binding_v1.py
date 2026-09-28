"""Non-operational CURRENT-instance proof; no custody operational entry is called."""
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / '.github/governance/evidence'
sys.path.insert(0, str(ROOT / 'tests'))
import p11_da_operational_consumer_v1 as C
import test_g77_256di_p11_da_operational_consumer_v1 as DI
from aigol.runtime.transport.serialization import replay_hash
from aigol.runtime.canonical_human_authority_act_contract_v1 import CanonicalHumanAuthorityActV1

def load(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m

FM = load(E/'g77_256fm_wrong_attempt_preboot_v1/launcher/sapianta_fresh_operation_context_v1.py', 'current_fm')
LG = load(E/'g77_256lg_wrong_scope_existing_route_admission_v1/adapter/G77_256LG_WRONG_SCOPE_VECTOR_ADAPTER_V1.py', 'current_lg')
LAUNCH = load(E/'g77_256fm_wrong_attempt_preboot_v1/launcher/G77_256FM_ONE_SHOT_QEMU_LAUNCHER_V1.py', 'current_launcher')
GEN = 'G77_256CURRENT_ONE_FRESH_HUMAN_AUTHORIZED_WRONG_SCOPE_OPERATIONAL_COMMISSIONING_V1'
OP = 'G77_256CURRENT_REPOSITORY_PROOF_001'

def context(vector='WRONG_SCOPE'):
    gen = GEN.replace('WRONG_SCOPE', vector)
    b = FM.materialize_preclaim_temporal_binding(repository_root=ROOT, generation_identity=gen, operation_identity=OP)
    return FM.seal_context(dict(context_schema_version=FM.SCHEMA_VERSION, generation_identity=gen, operation_identity=OP, preclaim_temporal_binding=b))

def reseal(c):
    c.pop('context_sha256', None)
    return FM.seal_context(c)

def temporal_schema():
    full = json.loads((E/'g77_256gd_fresh_operation_context_v1/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json').read_bytes())
    # Exact canonical temporal subschema and its generation-dependent rules.
    return {'type':'object', 'properties':{k:full['properties'][k] for k in ('generation_identity','preclaim_temporal_binding')}, 'allOf':full['allOf']}

@pytest.fixture(autouse=True)
def forbid_operations(monkeypatch):
    def forbidden(*a, **kw): pytest.fail('operational surface reached')
    for name in ('submit_human_act','claim_and_invoke_once','terminate_human_act'):
        monkeypatch.setattr(C.P11BoundedConsumerV1,name,forbidden)
    monkeypatch.setattr(C.ProtectedOwnerStateStoreV1,'initialize_available',forbidden)
    monkeypatch.setattr(C.ProtectedOwnerStateStoreV1,'claim_available',forbidden,raising=False)

def test_same_requirement_scope_only_native_validation(tmp_path):
    c=context();b,_=C.authenticate_preclaim_temporal_binding(c)
    jsonschema.validate(c,temporal_schema())
    instance=FM.authenticate_wrong_scope_current_instance(ROOT)
    for p,h in instance['sources'].items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
    assert b['coordinate_unix_ns']==500
    assert LG.current_temporal_coordinates(ROOT)==instance['temporal_coordinates']
    bindings=DI.FixedPrincipalBindings(os.getuid()+1,os.getuid()+2,os.getuid())
    store=SimpleNamespace(fixture_root=tmp_path,root_identity='synthetic-repository-owner')
    gate=DI._gate(store,bindings,context=c)
    er=LG.specialize_er_harness(ROOT)
    source=LG.specialize_fc_runtime_source(repository_root=ROOT,identity_namespace_prefix='G77_256CURRENT')
    ns={'__name__':'repository_only_guest','__file__':str(ROOT/LG.FC_ADAPTER)}
    exec(compile(source,ns['__file__'],'exec'),ns)
    result=ns['create_fc_input_and_authority'](er,gate,bindings,store)
    raw,record,act,correlation=result
    assert (act.payload['valid_from_unix_ns'],act.payload['valid_until_unix_ns'])==(100,1000)
    assert C.preclaim_temporal_decision(b,valid_from_unix_ns=100,valid_until_unix_ns=1000)=='CURRENT'
    consumer=object.__new__(C.P11BoundedConsumerV1);consumer._gate=gate;consumer._bindings=bindings
    # Positive baseline proves non-target payload and all source/correlation checks.
    valid=consumer._validate_authority_sources(act,correlation,record,owner_revision=0,now_unix_ns=500)
    assert valid.valid_from_unix_ns==100
    wrong=act.to_dict();wrong['authority_scope']=LG.PRESENTED_SCOPE
    wrong=CanonicalHumanAuthorityActV1.from_dict(wrong)
    corr=ns['rebind_canonical_correlation'](correlation,{'source_act_digest':replay_hash(wrong.to_dict())})
    assert [k for k in act.to_dict() if act.to_dict()[k]!=wrong.to_dict()[k]]==['authority_scope']
    with pytest.raises(C.FailClosedRuntimeError,match='scope is invalid'):
        consumer._validate_authority_sources(wrong,corr,record,owner_revision=0,now_unix_ns=500)
    assert not list(tmp_path.iterdir())
    # Submission override is fixed in the actual generated guest call, not a test override.
    tree=ast.parse(source)
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='submit_human_act']
    assert len(calls)==1
    assert next(k.value.value for k in calls[0].keywords if k.arg=='now_unix_ns')==500

@pytest.mark.parametrize('field,value', [('coordinate_unix_ns',1000),('coordinate_unix_ns',501),('coordinate_unix_ns',True),('vector_specification_path','other'),('vector_specification_sha256','0'*64),('vector_specification_identity','OTHER'),('policy_owner','OTHER'),('generation_identity','OTHER'),('operation_identity','OTHER')])
def test_both_validators_reject_resealed_substitution(field,value):
    c=context();c['preclaim_temporal_binding'][field]=value;c=reseal(c)
    with pytest.raises(FM.ContextError): FM.validate_preclaim_temporal_binding(c['preclaim_temporal_binding'],repository_root=ROOT,generation_identity=GEN,operation_identity=OP)
    with pytest.raises(C.FailClosedRuntimeError): C.authenticate_preclaim_temporal_binding(c)

@pytest.mark.parametrize('field,value',[('coordinate_unix_ns',1000),('vector_specification_sha256','0'*64),('vector_specification_path','other'),('vector_specification_identity','OTHER')])
def test_schema_rejects_other_instance(field,value):
    c=context();c['preclaim_temporal_binding'][field]=value
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(c,temporal_schema())

@pytest.mark.parametrize('time,expected',[(99,'FUTURE'),(100,'CURRENT'),(500,'CURRENT'),(999,'CURRENT'),(1000,'EXPIRED'),(1001,'EXPIRED')])
def test_existing_temporal_predicates(time,expected):
    assert C.preclaim_temporal_decision({'coordinate_unix_ns':time},valid_from_unix_ns=100,valid_until_unix_ns=1000)==expected

def test_expired_and_vector_swap():
    c=context('EXPIRED');b,_=C.authenticate_preclaim_temporal_binding(c)
    jsonschema.validate(c,temporal_schema());assert b['coordinate_unix_ns']==1000
    assert C.preclaim_temporal_decision(b,valid_from_unix_ns=100,valid_until_unix_ns=1000)=='EXPIRED'
    c['generation_identity']=GEN;c['preclaim_temporal_binding']['generation_identity']=GEN;c=reseal(c)
    with pytest.raises(C.FailClosedRuntimeError): C.authenticate_preclaim_temporal_binding(c)
    with pytest.raises(jsonschema.ValidationError): jsonschema.validate(c,temporal_schema())

def test_spec_corruption_fails_before_use(tmp_path):
    instance=FM.authenticate_wrong_scope_current_instance(ROOT)
    p=tmp_path/FM.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH;p.parent.mkdir(parents=True);p.write_text('{}')
    with pytest.raises(FM.ContextError): FM.authenticate_wrong_scope_current_instance(tmp_path)

def test_scope_and_temporal_predicate_source_unchanged():
    before=subprocess.check_output(['git','show','9a8f8b15:tests/p11_da_operational_consumer_v1.py'],cwd=ROOT).decode()
    after=(ROOT/'tests/p11_da_operational_consumer_v1.py').read_text()
    def selected(s):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(s)) if isinstance(n,ast.FunctionDef) and n.name in {'preclaim_temporal_decision','_validate_authority_sources','claim_and_invoke_once','submit_human_act','terminate_human_act'}}
    assert selected(before)==selected(after)

def test_current_checkout_hashes(tmp_path):
    # Real isolated Git objects prove the checkout selector without a VM or main-repo commit.
    paths=[LAUNCH.P11_CONSUMER_RELATIVE,FM.WRONG_SCOPE_ADAPTER_SOURCE_RELATIVE_PATH,FM.WRONG_SCOPE_CURRENT_SPECIFICATION_PATH,LAUNCH.CANDIDATE]+list(FM.authenticate_wrong_scope_current_instance(ROOT)['sources'])
    subprocess.run(['git','init','-q',str(tmp_path)],check=True)
    for p in paths:
        out=tmp_path/p;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/p).read_bytes())
    subprocess.run(['git','add','.'],cwd=tmp_path,check=True)
    subprocess.run(['git','-c','user.name=RepositoryProof','-c','user.email=proof@invalid','-c','core.hooksPath=/dev/null','commit','-qm','synthetic checkout proof'],cwd=tmp_path,check=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=tmp_path,text=True).strip();tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=tmp_path,text=True).strip()
    assert LAUNCH.governed_checkout_identity(tmp_path,'WRONG_SCOPE',head,tree)==(head,tree)
    full=LAUNCH.build_operation_context(repository_root=tmp_path,repository_head=head,repository_tree=tree,generation_identity=GEN,operation_identity=OP,identity_namespace_prefix='G77_256CURRENT',operation_evidence_root=tmp_path/'.github/governance/evidence/g77_256current_wrong_scope_current_v1/operation_state',transient_root=tmp_path/'transient')
    schema=json.loads((E/'g77_256gd_fresh_operation_context_v1/SAPIANTA_FRESH_OPERATION_CONTEXT_V1.schema.json').read_bytes())
    jsonschema.validate(full,schema)
    FM.validate_context(full,repository_root=tmp_path)
    assert C.authenticate_preclaim_temporal_binding(full)[0]['coordinate_unix_ns']==500
    (tmp_path/paths[0]).write_text('tampered')
    with pytest.raises(RuntimeError,match='binding mismatch'):LAUNCH.governed_checkout_identity(tmp_path,'WRONG_SCOPE',head,tree)
