const fs = require("fs");
const path = require("path");

if (process.platform !== "win32") process.exit(0);

const src = process.execPath; // 当前 node.exe 的绝对路径
const destDir = path.join(__dirname, "..", "node_modules", ".bin");
const dest = path.join(destDir, "node.exe");

try {
  if (!fs.existsSync(destDir)) process.exit(0);
  fs.copyFileSync(src, dest);
  console.log(`[fix] copied node.exe to ${dest}`);
} catch (e) {
  console.warn("[fix] failed to copy node.exe:", e.message);
}
