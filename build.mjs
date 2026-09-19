import fs from 'node:fs';
fs.mkdirSync('dist/server',{recursive:true});fs.mkdirSync('dist/.openai',{recursive:true});
fs.writeFileSync('dist/server/page.mjs','export const html='+JSON.stringify(fs.readFileSync('src/page.html','utf8'))+';');
fs.copyFileSync('src/search.mjs','dist/server/search.mjs');fs.copyFileSync('src/worker.mjs','dist/server/index.js');fs.copyFileSync('.openai/hosting.json','dist/.openai/hosting.json');
