const fs = require('fs');
const file = 'c:/Users/navka/.antigravity/extensions/ms-python.python-2026.4.0-universal/out/client/extension.js';
let content = fs.readFileSync(file, 'utf8');
const oldStr = 'try{const n=await e.initialize(t);if(false)throw new Error(`Unsupported position';
const newStr = 'try{const n=await e.initialize(t);if(n&&n.capabilities)n.capabilities.positionEncoding="utf-16";if(false)throw new Error(`Unsupported position';
content = content.replace(oldStr, newStr);
fs.writeFileSync(file, content);
