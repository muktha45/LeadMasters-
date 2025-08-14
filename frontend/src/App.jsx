import React, { useState, useEffect } from 'react'

const API = import.meta.env.VITE_API || 'http://localhost:8000'

function Login({ onToken }){
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  async function register(){
    const r = await fetch(API + '/auth/register', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email, password})
    })
    const data = await r.json()
    if(data.access_token){ onToken(data.access_token) }
    else alert(JSON.stringify(data))
  }

  async function login(){
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)
    const r = await fetch(API + '/auth/login', {
      method: 'POST',
      headers: {'Content-Type':'application/x-www-form-urlencoded'},
      body: params
    })
    const data = await r.json()
    if(data.access_token){ onToken(data.access_token) }
    else alert(JSON.stringify(data))
  }

  return (
    <div style={{border:'1px solid #ccc', padding:16, borderRadius:8, maxWidth:400}}>
      <h2>Login / Register</h2>
      <input placeholder="email" value={email} onChange={e=>setEmail(e.target.value)} style={{width:'100%',marginBottom:8}}/>
      <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} style={{width:'100%',marginBottom:8}}/>
      <div style={{display:'flex', gap:8}}>
        <button onClick={login}>Login</button>
        <button onClick={register}>Register</button>
      </div>
    </div>
  )
}

function Timer({ seconds, onEnd }){
  const [left, setLeft] = useState(seconds)
  useEffect(()=>{
    if(left <= 0){ onEnd(); return }
    const t = setTimeout(()=>setLeft(left-1), 1000)
    return ()=>clearTimeout(t)
  }, [left])
  const m = Math.floor(left/60).toString().padStart(2, '0')
  const s = (left%60).toString().padStart(2, '0')
  return <div style={{fontWeight:'bold'}}>Time: {m}:{s}</div>
}

function Exam({ token, onDone }){
  const [qs, setQs] = useState([])
  const [idx, setIdx] = useState(0)
  const [answers, setAnswers] = useState({})
  const [sessionId, setSessionId] = useState(null)

  useEffect(()=>{
    async function start(){
      const r = await fetch(API + '/exam/start?limit=5', {
        headers: {Authorization: 'Bearer ' + token}
      })
      const data = await r.json()
      if(data.session_id){
        setSessionId(data.session_id)
        setQs(data.questions)
      } else alert(JSON.stringify(data))
    }
    start()
  }, [])

  function setChoice(qid, ch){
    setAnswers(prev => ({...prev, [qid]: ch}))
  }

  async function submitNow(){
    const r = await fetch(API + '/exam/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer ' + token
      },
      body: JSON.stringify({session_id: sessionId, answers})
    })
    const data = await r.json()
    onDone(data)
  }

  if(qs.length === 0){
    return <div>Loading questions...</div>
  }

  const q = qs[idx]

  return (
    <div style={{maxWidth:700}}>
      <div style={{display:'flex', justifyContent:'space-between'}}>
        <h3>Exam</h3>
        <Timer seconds={30*60} onEnd={submitNow} />
      </div>
      <div style={{margin:'12px 0'}}>
        <div style={{marginBottom:8}}><b>Q{idx+1}.</b> {q.text}</div>
        {['a','b','c','d'].map(ch => (
          <label key={ch} style={{display:'block'}}>
            <input type="radio" name={'q'+q.id} checked={answers[q.id]===ch} onChange={()=>setChoice(q.id, ch)}/> {q['option_'+ch]}
          </label>
        ))}
      </div>
      <div style={{display:'flex', gap:8}}>
        <button disabled={idx===0} onClick={()=>setIdx(idx-1)}>Previous</button>
        <button disabled={idx===qs.length-1} onClick={()=>setIdx(idx+1)}>Next</button>
        <button onClick={submitNow} style={{marginLeft:'auto'}}>Submit</button>
      </div>
    </div>
  )
}

export default function App(){
  const [token, setToken] = useState(localStorage.getItem('token')||'')
  const [result, setResult] = useState(null)

  function onToken(t){
    localStorage.setItem('token', t)
    setToken(t)
  }

  if(result){
    return (
      <div style={{padding:16}}>
        <h2>Result</h2>
        <p>Score: {result.score} / {result.total}</p>
      </div>
    )
  }

  return (
    <div style={{padding:16}}>
      <h1>LeadMasters Student Exam</h1>
      {!token ? <Login onToken={onToken} /> : <Exam token={token} onDone={setResult} />}
    </div>
  )
}
