//! MemoryBackend trait for all storage backends.

use viki_core::{VikiError, RetrievalResult};
use serde_json::Value;

pub trait MemoryBackend: Send + Sync {
    fn backend_id(&self) -> &str;
    fn store(
        &self,
        content: &str,
        source: &str,
        metadata: Option<&Value>,
    ) -> Result<String, VikiError>;
    fn retrieve(
        &self,
        query: &str,
        top_k: usize,
    ) -> Result<Vec<RetrievalResult>, VikiError>;
    fn delete(&self, doc_id: &str) -> Result<bool, VikiError>;
    fn clear(&self) -> Result<(), VikiError>;
    fn count(&self) -> Result<usize, VikiError>;
}
