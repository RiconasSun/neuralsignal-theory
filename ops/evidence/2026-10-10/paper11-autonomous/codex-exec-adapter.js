// Preserve wrapper approval policy using the installed CLI's config interface.
const { spawn } = require('node:child_process');
const args = process.argv.slice(2);
const index = args.indexOf('--ask-for-approval');
if (index >= 0) {
  const policy = args[index + 1];
  if (!['on-request', 'untrusted', 'never'].includes(policy)) throw new Error('Invalid approval policy');
  args.splice(index, 2, '--config', `approval_policy="${policy}"`);
}
const child = spawn('C:/Users/85993/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe', args, { stdio: 'inherit', shell: false });
child.on('error', error => { process.stderr.write(String(error)); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
