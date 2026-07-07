ALTER TABLE document_chunks
DROP COLUMN embedding;

ALTER TABLE document_chunks
ADD COLUMN embedding vector(768);