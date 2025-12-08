import { useState } from 'react'
import { ingestDocuments } from '../api/ragService'

/**
 * Sidebar Component
 * 
 * Admin tools and settings panel
 */
function Sidebar({ isOpen, onClose, stats }) {
    const [isIngesting, setIsIngesting] = useState(false)
    const [ingestResult, setIngestResult] = useState(null)

    const handleIngest = async () => {
        setIsIngesting(true)
        setIngestResult(null)

        try {
            const result = await ingestDocuments()
            setIngestResult({ success: true, message: result.message })
        } catch (err) {
            setIngestResult({ success: false, message: err.message })
        } finally {
            setIsIngesting(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="sidebar-overlay" onClick={onClose}>
            <aside className="sidebar" onClick={e => e.stopPropagation()}>
                <div className="sidebar-header">
                    <h2>Settings</h2>
                    <button className="sidebar-close" onClick={onClose}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="18" y1="6" x2="6" y2="18" />
                            <line x1="6" y1="6" x2="18" y2="18" />
                        </svg>
                    </button>
                </div>

                <div className="sidebar-content">
                    <section className="sidebar-section">
                        <h3>System Status</h3>
                        <div className="status-grid">
                            <div className="status-item">
                                <span className="status-label">Vector Store</span>
                                <span className="status-value">ChromaDB</span>
                            </div>
                            <div className="status-item">
                                <span className="status-label">LLM</span>
                                <span className="status-value">LaMini-Flan-T5</span>
                            </div>
                            {stats && (
                                <div className="status-item">
                                    <span className="status-label">Documents</span>
                                    <span className="status-value">{stats.total_chunks} chunks</span>
                                </div>
                            )}
                        </div>
                    </section>

                    <section className="sidebar-section">
                        <h3>Admin Tools</h3>
                        <button
                            className="admin-button"
                            onClick={handleIngest}
                            disabled={isIngesting}
                        >
                            {isIngesting ? 'Ingesting...' : 'Re-ingest Knowledge Base'}
                        </button>

                        {ingestResult && (
                            <div className={`ingest-result ${ingestResult.success ? 'success' : 'error'}`}>
                                {ingestResult.message}
                            </div>
                        )}
                    </section>
                </div>
            </aside>
        </div>
    )
}

export default Sidebar
