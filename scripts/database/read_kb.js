// Quick Knowledge Base Reader using Node.js
// No external deps needed - uses sql.js from CDN or built-in if available

const fs = require('fs');
const path = require('path');

// Simple SQLite parser - reads raw database
function readSQLiteDB(dbPath) {
    try {
        const buffer = fs.readFileSync(dbPath);

        // SQLite format: Look for text strings in the raw data
        const text = buffer.toString('utf8', 0, buffer.length);

        // Extract documents table content
        const docs = [];

        // Simple regex to find JSON-like metadata and content
        const contentMatches = text.match(/\{[^}]*"type"[^}]*\}[^{]*?(?=\{|$)/g);

        if (contentMatches) {
            contentMatches.forEach((match, i) => {
                const metaMatch = match.match(/\{[^}]*\}/);
                const content = match.slice(metaMatch ? metaMatch[0].length : 0).trim();

                if (content.length > 20) {
                    docs.push({
                        id: i + 1,
                        metadata: metaMatch ? metaMatch[0] : '',
                        content: content.slice(0, 500)
                    });
                }
            });
        }

        return docs;
    } catch (error) {
        console.error('Error reading database:', error.message);
        return [];
    }
}

// Read the private knowledge base
const privateDB = path.join(__dirname, 'Assets', 'Synthesis.Pro', 'Server', 'synthesis_private.db');

if (!fs.existsSync(privateDB)) {
    console.error('Private DB not found:', privateDB);
    process.exit(1);
}

console.log('Reading Private Knowledge Base...\n');
console.log('='.repeat(70));

const stats = fs.statSync(privateDB);
console.log(`Database: ${path.basename(privateDB)}`);
console.log(`Size: ${(stats.size / 1024).toFixed(2)} KB`);
console.log(`Modified: ${stats.mtime.toISOString()}`);
console.log('='.repeat(70));
console.log();

// Try to extract readable content
const docs = readSQLiteDB(privateDB);

if (docs.length > 0) {
    console.log(`Found ${docs.length} document fragments:\n`);
    docs.forEach(doc => {
        if (doc.metadata) console.log(`Metadata: ${doc.metadata}`);
        console.log(`Content: ${doc.content}...`);
        console.log('-'.repeat(70));
    });
} else {
    console.log('No documents found with simple parsing.');
    console.log('\nTrying to install better-sqlite3 for proper querying...');

    // Try npm install
    const { execSync } = require('child_process');
    try {
        console.log('Running: npm install better-sqlite3');
        execSync('npm install better-sqlite3', { stdio: 'inherit', cwd: __dirname });
        console.log('\nRe-run this script to query the database properly.');
    } catch (e) {
        console.error('\nCould not install better-sqlite3.');
        console.error('Run manually: npm install better-sqlite3');
    }
}
