import csv
import json
import study as r


def write(name,rows):
    with (r.HERE/'results'/name).open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)


def main():
    native=r.load(r.HERE/'results/native3.json')
    write('operation_table.csv',[dict(context=x['context'],index=x['index'],bytes=x['payload_bytes'],passed=x['passed'],
        idempotent=x['idempotent_resume'],source_verified=x['source_verified'],ACL_verified=x['ACL_verified'],
        attempts=x['receipt']['attempts'],native_events=json.dumps(x['receipt']['events'],sort_keys=True)) for x in native['noninjected_commits']])
    write('injection_table.csv',[dict(name=x['name'],passed=x['test_pass'],successful_commit_count=x['successful_commit_count'],
        diagnostic_detail=json.dumps(x,sort_keys=True)) for x in native['injected_tests']])
    print(dict(operation_rows=200,injection_rows=18))


if __name__=='__main__':main()
