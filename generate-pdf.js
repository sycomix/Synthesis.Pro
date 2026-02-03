const fs = require('fs');
const path = require('path');

// Markdown files to include in order
const files = [
    'README.md',
    'Assets/Synthesis.Pro/Documentation/User/INSTALLATION.md',
    'EFFICIENT_WORKFLOW.md',
    'Assets/Synthesis.Pro/Documentation/User/CHANGELOG.md',
    'Assets/Synthesis.Pro/Documentation/User/CONTRIBUTING.md',
    'Assets/Synthesis.Pro/Documentation/User/CREDITS.md'
];

console.log('[PDF Generator] Combining markdown files...');

let combinedMarkdown = '';

// Add title page
combinedMarkdown += `# Synthesis.Pro User Documentation

**Version 1.1.0-beta**

AI Collaboration for Unity Development with Privacy-First Architecture

---

`;

// Read and combine all files
files.forEach((file, index) => {
    const filePath = path.join(__dirname, file);

    if (fs.existsSync(filePath)) {
        console.log(`[PDF Generator] Adding: ${file}`);

        const content = fs.readFileSync(filePath, 'utf8');

        // Add page break before each new document (except first)
        if (index > 0) {
            combinedMarkdown += '\n\n---\n\n<div style="page-break-after: always;"></div>\n\n';
        }

        // Add the file content
        combinedMarkdown += content + '\n\n';
    } else {
        console.log(`[PDF Generator] Warning: File not found: ${file}`);
    }
});

// Save combined markdown
const outputMd = path.join(__dirname, 'Synthesis.Pro-Documentation.md');
fs.writeFileSync(outputMd, combinedMarkdown);
console.log(`[PDF Generator] ✅ Combined markdown saved: ${outputMd}`);

// Create HTML version for browser-based PDF generation
const html = `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Synthesis.Pro Documentation</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #24292e;
        }
        h1 {
            color: #0366d6;
            border-bottom: 2px solid #0366d6;
            padding-bottom: 10px;
            margin-top: 40px;
        }
        h2 {
            color: #0366d6;
            border-bottom: 1px solid #e1e4e8;
            padding-bottom: 8px;
            margin-top: 30px;
        }
        h3 {
            color: #24292e;
            margin-top: 24px;
        }
        code {
            background: #f6f8fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
        }
        pre {
            background: #f6f8fa;
            padding: 16px;
            border-radius: 6px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            padding: 0;
        }
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            color: #6a737d;
            margin: 0;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 16px 0;
        }
        th, td {
            border: 1px solid #dfe2e5;
            padding: 8px 12px;
            text-align: left;
        }
        th {
            background: #f6f8fa;
            font-weight: 600;
        }
        a {
            color: #0366d6;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .page-break {
            page-break-after: always;
        }
        @media print {
            body {
                max-width: none;
            }
        }
    </style>
</head>
<body>
<div id="content"></div>
<script>
const markdown = ${JSON.stringify(combinedMarkdown)};

// Simple markdown to HTML conversion
function convertMarkdown(md) {
    // Headers
    md = md.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    md = md.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    md = md.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold
    md = md.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>');

    // Italic
    md = md.replace(/\\*(.*?)\\*/g, '<em>$1</em>');

    // Code blocks
    md = md.replace(/\`\`\`([\\s\\S]*?)\`\`\`/g, '<pre><code>$1</code></pre>');

    // Inline code
    md = md.replace(/\`(.*?)\`/g, '<code>$1</code>');

    // Links
    md = md.replace(/\\[([^\\]]+)\\]\\(([^\\)]+)\\)/g, '<a href="$2">$1</a>');

    // Line breaks
    md = md.replace(/\\n\\n/g, '</p><p>');
    md = md.replace(/\\n/g, '<br>');

    // Horizontal rules
    md = md.replace(/^---$/gm, '<hr>');

    // Page breaks
    md = md.replace(/<div style="page-break-after: always;"><\\/div>/g, '<div class="page-break"></div>');

    return '<p>' + md + '</p>';
}

document.getElementById('content').innerHTML = convertMarkdown(markdown);

// Auto-print dialog for PDF generation
window.onload = function() {
    console.log('Documentation loaded. Press Ctrl+P to print to PDF.');
};
</script>
</body>
</html>`;

const outputHtml = path.join(__dirname, 'Synthesis.Pro-Documentation.html');
fs.writeFileSync(outputHtml, html);
console.log(`[PDF Generator] ✅ HTML version saved: ${outputHtml}`);

console.log('\n[PDF Generator] Next steps:');
console.log('1. Open Synthesis.Pro-Documentation.html in your browser');
console.log('2. Press Ctrl+P (or Cmd+P on Mac)');
console.log('3. Select "Save as PDF" as the destination');
console.log('4. Save as: Synthesis.Pro-User-Guide.pdf');
console.log('\nOr install a package for automated PDF generation:');
console.log('  npm install -g md-to-pdf');
console.log('  md-to-pdf Synthesis.Pro-Documentation.md');
