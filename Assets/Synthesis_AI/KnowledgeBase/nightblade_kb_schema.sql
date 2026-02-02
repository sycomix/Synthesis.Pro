-- NightBlade Knowledge Base Schema
-- Stores all documentation in searchable SQLite database

-- Main documentation entries
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    category TEXT, -- core-systems, performance, networking, troubleshooting, etc.
    full_path TEXT NOT NULL,
    content TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    word_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document sections (for fine-grained searching)
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    heading TEXT NOT NULL,
    level INTEGER NOT NULL, -- h1=1, h2=2, h3=3, etc.
    content TEXT NOT NULL,
    section_order INTEGER NOT NULL, -- order within document
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Code examples extracted from docs
CREATE TABLE IF NOT EXISTS code_examples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    section_id INTEGER,
    language TEXT, -- csharp, bash, json, etc.
    code TEXT NOT NULL,
    description TEXT,
    line_number INTEGER,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);

-- API/Class documentation
CREATE TABLE IF NOT EXISTS api_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    class_name TEXT,
    method_name TEXT,
    property_name TEXT,
    description TEXT NOT NULL,
    parameters TEXT, -- JSON array of parameters
    return_type TEXT,
    example_usage TEXT,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Troubleshooting entries
CREATE TABLE IF NOT EXISTS troubleshooting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    symptom TEXT NOT NULL,
    cause TEXT,
    solution TEXT NOT NULL,
    severity TEXT DEFAULT 'medium', -- low, medium, high, critical
    tags TEXT, -- comma-separated: network, performance, ui, etc.
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Architecture concepts
CREATE TABLE IF NOT EXISTS architecture (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    concept_name TEXT NOT NULL,
    description TEXT NOT NULL,
    diagram TEXT, -- ASCII diagram or path to image
    related_systems TEXT, -- comma-separated system names
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Configuration options
CREATE TABLE IF NOT EXISTS configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    setting_name TEXT NOT NULL,
    setting_type TEXT, -- string, int, bool, object
    default_value TEXT,
    description TEXT NOT NULL,
    example TEXT,
    related_to TEXT, -- component/system name
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

-- Search tags for quick filtering
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT, -- system, performance, network, ui, etc.
    usage_count INTEGER DEFAULT 0
);

-- Tag associations
CREATE TABLE IF NOT EXISTS document_tags (
    document_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (document_id, tag_id),
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Changelog entries (version history)
CREATE TABLE IF NOT EXISTS changelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    release_date TEXT,
    entry_type TEXT, -- feature, bugfix, breaking, deprecation
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    related_documents TEXT, -- comma-separated document IDs
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Quick reference/cheatsheet entries
CREATE TABLE IF NOT EXISTS quick_reference (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    command TEXT,
    description TEXT NOT NULL,
    example TEXT,
    related_doc_id INTEGER,
    FOREIGN KEY (related_doc_id) REFERENCES documents(id) ON DELETE SET NULL
);

-- Indexes for fast searching
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_title ON documents(title);
CREATE INDEX IF NOT EXISTS idx_sections_heading ON sections(heading);
CREATE INDEX IF NOT EXISTS idx_api_class ON api_references(class_name);
CREATE INDEX IF NOT EXISTS idx_api_method ON api_references(method_name);
CREATE INDEX IF NOT EXISTS idx_troubleshooting_symptom ON troubleshooting(symptom);
CREATE INDEX IF NOT EXISTS idx_architecture_concept ON architecture(concept_name);
CREATE INDEX IF NOT EXISTS idx_configurations_name ON configurations(setting_name);
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_changelog_version ON changelog(version);

-- Full-text search virtual tables (for fast content search)
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    filename, title, content, category,
    content=documents,
    content_rowid=id
);

CREATE VIRTUAL TABLE IF NOT EXISTS sections_fts USING fts5(
    heading, content,
    content=sections,
    content_rowid=id
);

-- Triggers to keep FTS tables in sync
CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
    INSERT INTO documents_fts(rowid, filename, title, content, category)
    VALUES (new.id, new.filename, new.title, new.content, new.category);
END;

CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
    DELETE FROM documents_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
    UPDATE documents_fts 
    SET filename = new.filename, 
        title = new.title, 
        content = new.content,
        category = new.category
    WHERE rowid = new.id;
END;

CREATE TRIGGER IF NOT EXISTS sections_ai AFTER INSERT ON sections BEGIN
    INSERT INTO sections_fts(rowid, heading, content)
    VALUES (new.id, new.heading, new.content);
END;

CREATE TRIGGER IF NOT EXISTS sections_ad AFTER DELETE ON sections BEGIN
    DELETE FROM sections_fts WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS sections_au AFTER UPDATE ON sections BEGIN
    UPDATE sections_fts 
    SET heading = new.heading, 
        content = new.content
    WHERE rowid = new.id;
END;
