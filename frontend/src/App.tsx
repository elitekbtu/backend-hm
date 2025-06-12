import React, { useState } from 'react'
import './App.css'

const providers = ['openai', 'gemini'] as const

type Provider = typeof providers[number]

interface ChatMessage {
  role: 'user' | 'ai'
  content: string
}

interface EndpointTest {
  label: string
  path: string
  method: 'GET' | 'POST'
}

const testEndpoints: EndpointTest[] = [
  { label: 'Root /', path: '/', method: 'GET' },
  { label: 'Health', path: '/health', method: 'GET' },
  { label: 'Start Task', path: '/start-task', method: 'POST' },
]

function App() {
  const [provider, setProvider] = useState<Provider>('openai')
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [endpointResult, setEndpointResult] = useState<string>('')

  const sendMessage = async () => {
    if (!prompt.trim()) return

    const userMsg: ChatMessage = { role: 'user', content: prompt }
    setMessages((prev: ChatMessage[]) => [...prev, userMsg])
    setPrompt('')
    setLoading(true)

    try {
      const res = await fetch(`http://localhost:8000/chat/${provider}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userMsg.content }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || res.statusText)
      }

      const data = await res.json()
      const aiMsg: ChatMessage = { role: 'ai', content: data.response }
      setMessages((prev: ChatMessage[]) => [...prev, aiMsg])
    } catch (err: any) {
      setMessages((prev: ChatMessage[]) => [...prev, { role: 'ai', content: `Error: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  const testEndpoint = async (ep: EndpointTest) => {
    setEndpointResult('')
    try {
      const res = await fetch(`http://localhost:8000${ep.path}`, {
        method: ep.method,
        headers: { 'Content-Type': 'application/json' },
      })
      const data = await res.json().catch(() => ({}))
      setEndpointResult(JSON.stringify(data))
    } catch (err: any) {
      setEndpointResult(`Error: ${err.message}`)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      sendMessage()
    }
  }

  return (
    <>
    <div className="navbar">
      {testEndpoints.map((ep) => (
        <button key={ep.label} onClick={() => testEndpoint(ep)}>
          {ep.label}
        </button>
      ))}
    </div>

    <div className="endpoint-result">{endpointResult}</div>

    <div className="chat-container">
      <h1 className="title">AI Chat Client</h1>

      <div className="provider-select">
        <label htmlFor="provider">Provider:</label>
        <select
          id="provider"
          value={provider}
          onChange={(e) => setProvider(e.target.value as Provider)}
        >
          {providers.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {loading && <div className="message ai">...</div>}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
    </>
  )
}

export default App
