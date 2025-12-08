/**
 * Source Cards Component
 * 
 * Displays the source documents used to generate the answer
 */
function SourceCards({ sources }) {
    if (!sources || sources.length === 0) {
        return null
    }

    return (
        <div className="sources-section" style={{ padding: '0 1.5rem 1.5rem' }}>
            <h4 className="sources-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                    <line x1="16" y1="13" x2="8" y2="13" />
                    <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
                Sources ({sources.length})
            </h4>
            <div className="sources-list">
                {sources.map((source, index) => (
                    <div key={index} className="source-card">
                        <div className="source-title">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                                <polyline points="13 2 13 9 20 9" />
                            </svg>
                            {source.source}
                            {source.chunk_index !== null && source.chunk_index !== undefined && (
                                <span className="source-chunk-badge">
                                    Chunk {source.chunk_index + 1}
                                </span>
                            )}
                        </div>
                        <p className="source-excerpt">{source.content}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default SourceCards
