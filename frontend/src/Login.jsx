import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'

function Login({ setToken }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate() // Πιο σωστό από το window.location

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    try {
      const response = await axios.post('https://xristinakoufi.onrender.com/users/login', formData)
      const token = response.data.access_token
      localStorage.setItem('token', token)
      setToken(token)
      navigate('/') // Σε στέλνει στην αρχική χωρίς refresh
    } catch (err) {
      setError('Λάθος username ή κωδικός! Δοκιμάστε ξανά.')
    }
  }

  return (
    <div className="container mt-5">
      <div className="row justify-content-center">
        <div className="col-md-5">
          <div className="card shadow border-0 p-4">
            <h3 className="text-center mb-4 fw-bold text-primary">Είσοδος Χρήστη</h3>
            {error && <div className="alert alert-danger">{error}</div>}
            <form onSubmit={handleLogin}>
              <div className="mb-3">
                <label className="form-label fw-semibold">Όνομα Χρήστη</label>
                <input 
                  type="text" 
                  className="form-control" 
                  value={username} 
                  onChange={(e) => setUsername(e.target.value)} 
                  required 
                />
              </div>
              <div className="mb-3">
                <label className="form-label fw-semibold">Κωδικός Πρόσβασης</label>
                <input 
                  type="password" 
                  className="form-control" 
                  value={password} 
                  onChange={(e) => setPassword(e.target.value)} 
                  required 
                />
              </div>
              <button type="submit" className="btn btn-primary w-100 py-2 fw-bold">
                Σύνδεση
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login
