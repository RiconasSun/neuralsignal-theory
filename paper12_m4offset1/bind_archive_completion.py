"""Append completion binding to the existing closure; no status/source rewrite."""
import study as r
from closure_verify import bind_completion,verify


def main():
    record=r.load(r.HERE/'closure_registration.json')
    r.save(r.HERE/'closure_completion_binding.json',dict(utc=r.datetime.now(r.timezone.utc).isoformat(),
        closure_registration_sha256=r.sha(r.HERE/'closure_registration.json'),completed_failure_bindings=bind_completion(record),
        scope='Append missing completed-native receipt binding; original status prefix and scientific failure unchanged'),True)
    verify();print('COMPLETED_NATIVE_STOP_BOUND; STATUS_AND_SCIENCE_UNCHANGED')


if __name__=='__main__':main()
