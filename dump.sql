BEGIN TRANSACTION;
CREATE TABLE memories (
                id TEXT PRIMARY KEY,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                accessed_at REAL NOT NULL,
                access_count INTEGER NOT NULL DEFAULT 0,
                priority INTEGER NOT NULL DEFAULT 50,
                tags TEXT NOT NULL DEFAULT '[]',
                source TEXT NOT NULL DEFAULT '',
                confidence REAL NOT NULL DEFAULT 1.0,
                expires_at REAL,
                -- Type-specific fields
                session_id TEXT,
                turn_index INTEGER DEFAULT 0,
                related_entries TEXT DEFAULT '[]',
                event_type TEXT,
                participants TEXT DEFAULT '[]',
                location TEXT,
                duration_seconds REAL DEFAULT 0,
                outcome TEXT,
                emotions TEXT DEFAULT '{}',
                category TEXT,
                entities TEXT DEFAULT '[]',
                relations TEXT DEFAULT '[]',
                provenance TEXT,
                verification_status TEXT DEFAULT 'unverified',
                supersedes TEXT DEFAULT '[]',
                skill_name TEXT,
                steps TEXT DEFAULT '[]',
                preconditions TEXT DEFAULT '[]',
                postconditions TEXT DEFAULT '[]',
                tools_required TEXT DEFAULT '[]',
                success_rate REAL DEFAULT 0,
                execution_count INTEGER DEFAULT 0,
                last_executed REAL,
                version INTEGER DEFAULT 1,
                preference_key TEXT,
                preference_value TEXT,
                scope TEXT DEFAULT 'global',
                overridden_by TEXT
            );
PRAGMA writable_schema=ON;
INSERT INTO sqlite_master(type,name,tbl_name,rootpage,sql)VALUES('table','memories_fts','memories_fts',0,'CREATE VIRTUAL TABLE memories_fts
                    USING fts5(content, tags, metadata, source, tokenize=''porter unicode61'')');
CREATE TABLE 'memories_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
INSERT INTO "memories_fts_config" VALUES('version',4);
CREATE TABLE 'memories_fts_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3);
CREATE TABLE 'memories_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
INSERT INTO "memories_fts_data" VALUES(1,X'');
INSERT INTO "memories_fts_data" VALUES(10,X'00000000000000');
CREATE TABLE 'memories_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE 'memories_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE schema_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
INSERT INTO "schema_info" VALUES('version','2');
CREATE INDEX idx_mem_type ON memories(memory_type);
CREATE INDEX idx_mem_created ON memories(created_at);
CREATE INDEX idx_mem_accessed ON memories(accessed_at);
CREATE INDEX idx_mem_priority ON memories(priority);
CREATE INDEX idx_mem_tags ON memories(tags);
CREATE INDEX idx_mem_source ON memories(source);
CREATE INDEX idx_mem_expires ON memories(expires_at);
CREATE INDEX idx_mem_session ON memories(session_id);
CREATE TRIGGER memories_fts_insert
                    AFTER INSERT ON memories BEGIN
                        INSERT INTO memories_fts(rowid, content, tags, metadata, source)
                        VALUES (new.id, new.content, new.tags, new.metadata, new.source);
                    END;
CREATE TRIGGER memories_fts_delete
                    AFTER DELETE ON memories BEGIN
                        DELETE FROM memories_fts WHERE rowid = old.id;
                    END;
CREATE TRIGGER memories_fts_update
                    AFTER UPDATE ON memories BEGIN
                        DELETE FROM memories_fts WHERE rowid = old.id;
                        INSERT INTO memories_fts(rowid, content, tags, metadata, source)
                        VALUES (new.id, new.content, new.tags, new.metadata, new.source);
                    END;
PRAGMA writable_schema=OFF;
COMMIT;
