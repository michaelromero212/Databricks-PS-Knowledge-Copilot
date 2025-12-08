import { useState, useEffect } from 'react'
import { useRAG } from './hooks/useRAG'
import { checkHealth } from './api/ragService'
import ChatInterface from './components/ChatInterface'
import SourceCards from './components/SourceCards'
import Sidebar from './components/Sidebar'

function App() {
    const { query, isLoading, error, result, history } = useRAG()
    const [isHealthy, setIsHealthy] = useState(null)
    const [stats, setStats] = useState(null)

    // Check API health on mount
    useEffect(() => {
        checkHealth()
            .then(data => {
                setIsHealthy(data.status === 'healthy')
                setStats(data)
            })
            .catch(() => setIsHealthy(false))
    }, [])

    const handleQuery = async (queryText) => {
        await query(queryText)
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <div className="header-title">
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                            <rect width="32" height="32" rx="6" fill="#FF3621" />
                            <path d="M8 12L16 8L24 12V20L16 24L8 20V12Z" fill="white" />
                            <path d="M16 8V16M16 16L8 12M16 16L24 12M16 16V24" stroke="#FF3621" strokeWidth="1.5" />
                        </svg>
                        <div>
                            <h1>PS Knowledge Copilot</h1>
                            <p className="header-subtitle">Databricks Professional Services</p>
                        </div>
                    </div>
                    <div className="header-status">
                        <span className={`status-dot ${isHealthy === false ? 'offline' : ''}`}
                            style={{ backgroundColor: isHealthy === false ? '#DC2626' : '#00A972' }} />
                        <span>{isHealthy === null ? 'Checking...' : isHealthy ? 'Online' : 'Offline'}</span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="app-main">
                {/* Query Card */}
                <ChatInterface
                    onQuery={handleQuery}
                    isLoading={isLoading}
                    error={error}
                />

                {/* Answer Display */}
                {result && (
                    <div className="answer-section">
                        <div className="answer-header">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                            </svg>
                            <h3>Answer</h3>
                        </div>
                        <div className="answer-content">
                            <p className="answer-text">{result.answer}</p>

                            <div className="answer-meta">
                                <span>Provider: {result.provider}</span>
                                {result.processing_time_ms && (
                                    <span>Time: {result.processing_time_ms.toFixed(0)}ms</span>
                                )}
                            </div>
                        </div>

                        {/* Sources */}
                        {result.sources && result.sources.length > 0 && (
                            <SourceCards sources={result.sources} />
                        )}
                    </div>
                )}

                {/* Empty State */}
                {!result && !isLoading && !error && (
                    <div className="empty-state">
                        <svg className="empty-state-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                            <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        <h3>Ask a Question</h3>
                        <p>Enter a question about Databricks best practices, architecture, or optimization.</p>

                        <QuickActions onSelect={handleQuery} />
                    </div>
                )}

                {/* Loading State */}
                {isLoading && (
                    <div className="loading-container">
                        <div className="loading-spinner" />
                        <p className="loading-text">Searching knowledge base...</p>
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <div className="footer-content">
                    <p>Databricks PS Knowledge Copilot • Powered by RAG + LLM</p>
                </div>
            </footer>
        </div>
    )
}

function QuickActions({ onSelect }) {
    const quickQueries = [
        "How do I optimize MERGE performance?",
        "What are Unity Catalog best practices?",
        "When should I recommend Photon?",
        "How does Auto Loader handle schema evolution?",
    ]

    return (
        <div className="quick-actions">
            <p className="quick-actions-title">Try these questions:</p>
            <div className="quick-actions-list">
                {quickQueries.map((q, i) => (
                    <button key={i} className="quick-action-btn" onClick={() => onSelect(q)}>
                        {q}
                    </button>
                ))}
            </div>
        </div>
    )
}

export default App
