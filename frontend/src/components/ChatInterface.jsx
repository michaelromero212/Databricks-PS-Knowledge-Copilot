import { useState } from 'react'

/**
 * Chat Interface Component
 * 
 * Provides the query input form with loading and error states
 */
function ChatInterface({ onQuery, isLoading, error }) {
    const [inputValue, setInputValue] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        if (inputValue.trim() && !isLoading) {
            onQuery(inputValue.trim())
        }
    }

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
        }
    }

    return (
        <div className="query-card">
            <h2>Ask a Question</h2>
            <form className="query-form" onSubmit={handleSubmit}>
                <input
                    type="text"
                    className="query-input"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="e.g., How do I optimize MERGE performance?"
                    disabled={isLoading}
                    aria-label="Enter your question"
                />
                <button
                    type="submit"
                    className={`query-button ${isLoading ? 'loading' : ''}`}
                    disabled={isLoading || !inputValue.trim()}
                >
                    {isLoading ? (
                        <>
                            <span className="loading-spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                            Thinking...
                        </>
                    ) : (
                        <>
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="11" cy="11" r="8" />
                                <line x1="21" y1="21" x2="16.65" y2="16.65" />
                            </svg>
                            Ask
                        </>
                    )}
                </button>
            </form>

            {error && (
                <div className="error-message" style={{ marginTop: '1rem' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                    {error}
                </div>
            )}
        </div>
    )
}

export default ChatInterface
