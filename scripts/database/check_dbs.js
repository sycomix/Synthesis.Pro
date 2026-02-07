const fs = require('fs');
const path = require('path');

const serverDir = path.join(__dirname, 'Assets', 'Synthesis.Pro', 'Server');
const dbs = ['synthesis_private.db', 'synthesis_public.db'];

console.log('Database Status:');
console.log('='.repeat(60));

dbs.forEach(db => {
    const dbPath = path.join(serverDir, db);
    if (fs.existsSync(dbPath)) {
        const stats = fs.statSync(dbPath);
        console.log(`✓ ${db}: ${(stats.size/1024).toFixed(2)}KB`);
        console.log(`  Modified: ${stats.mtime.toISOString()}`);
    } else {
        console.log(`✗ ${db}: MISSING`);
    }
});
