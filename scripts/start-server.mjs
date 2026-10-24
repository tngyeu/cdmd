import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { stripVTControlCharacters } from 'node:util';

if (Number(process.versions.node.split('.')[0]) < 20) {
  console.error('Cần Node.js 20 trở lên để chạy site.');
  process.exit(1);
}

const projectRoot = fileURLToPath(new URL('../', import.meta.url));
const openBrowser = !process.argv.includes('--no-open');
let output = '', opened = false, stopping = false;

console.log('Đang khởi động Sổ tay đất đai Ninh Bình…');
console.log('Giữ cửa sổ này mở để sử dụng site. Nhấn Ctrl+C để dừng server.\n');

const server = spawn(process.execPath, [path.join(projectRoot, 'node_modules/@11ty/eleventy/cmd.cjs'), '--serve', '--port=8080'], {
  cwd: projectRoot,
  stdio: ['inherit', 'pipe', 'pipe']
});

function relay(chunk, stream) {
  stream.write(chunk);
  output = (output + chunk.toString()).slice(-4096);
  const ready = stripVTControlCharacters(output).match(/Server at\s+(http:\/\/(?:localhost|127\.0\.0\.1):\d+\/)/);
  if (!ready || opened) return;
  opened = true;
  const url = new URL(ready[1]);
  url.hostname = '127.0.0.1';
  console.log(`\nMở site: ${url.href}\n`);
  if (openBrowser) {
    const browser = spawn('cmd.exe', ['/d', '/c', 'start', url.href], { windowsHide: true, stdio: 'ignore' });
    browser.on('error', () => console.warn(`Hãy mở trình duyệt tại ${url.href}`));
    browser.unref();
  }
}
server.stdout.on('data', chunk => relay(chunk, process.stdout));
server.stderr.on('data', chunk => relay(chunk, process.stderr));

server.on('error', error => {
  console.error(`Không khởi động được server: ${error.message}`);
  process.exitCode = 1;
});
server.on('close', code => { process.exitCode = stopping ? 0 : (code ?? 1); });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => {
  stopping = true;
  if (!server.killed) server.kill(signal);
});
