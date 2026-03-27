import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import axios from 'axios'
import Login from './Login'
import MyBookings from './MyBookings' // Βεβαιώσου ότι έχεις φτιάξει αυτό το αρχείο

function App() {
  const [events, setEvents] = useState([])
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = () => {
    axios.get('http://localhost:8000/events/')
      .then(res => setEvents(res.data))
      .catch(err => console.error(err))
  }

  const handleBooking = async (ticketTypeId) => {
    try {
      await axios.post('http://localhost:8000/bookings/', 
        { ticket_type_id: ticketTypeId, quantity: 1 }, 
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alert("Η κράτηση ολοκληρώθηκε επιτυχώς!")
      fetchData() 
    } catch (err) {
      alert("Σφάλμα κατά την κράτηση. Ίσως εξαντλήθηκαν τα εισιτήρια.")
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
  }

  return (
    <Router>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4 shadow">
        <div className="container">
          <Link className="navbar-brand fw-bold" to="/">📅 EventApp</Link>
          <div className="navbar-nav me-auto">
            {token && (
              <Link className="nav-link" to="/my-bookings">Οι Κρατήσεις μου</Link>
            )}
          </div>
          <div>
            {token ? (
              <button onClick={logout} className="btn btn-danger btn-sm">Logout</button>
            ) : (
              <Link className="btn btn-primary btn-sm" to="/login">Login</Link>
            )}
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={
          <div className="container">
            <h2 className="mb-4">Διαθέσιμες Εκδηλώσεις</h2>
            <div className="row">
              {events.map(event => (
                <div key={event.id} className="col-md-6 col-lg-4 mb-4">
                  <div className="card h-100 shadow-sm border-0">
                    <div className="card-body">
                      <h5 className="card-title fw-bold">{event.title}</h5>
                      <p className="text-muted small">📍 {event.venue}, {event.city}</p>
                      <p className="card-text text-secondary">{event.description}</p>
                      
                      <div className="mt-3">
                        <h6>Εισιτήρια:</h6>
                        {event.ticket_types && event.ticket_types.length > 0 ? (
                          event.ticket_types.map(ticket => (
                            <div key={ticket.id} className="p-2 border rounded mb-2 d-flex justify-content-between align-items-center bg-light">
                              <div>
                                <strong>{ticket.name}</strong> - {ticket.price}€
                                <br/><small className="text-success">Διαθέσιμα: {ticket.available}</small>
                              </div>
                              <button 
                                className="btn btn-sm btn-success" 
                                disabled={!token || ticket.available <= 0}
                                onClick={() => handleBooking(ticket.id)}
                              >
                                {token ? "Κράτηση" : "Login"}
                              </button>
                            </div>
                          ))
                        ) : (
                          <p className="small text-danger">Δεν υπάρχουν διαθέσιμοι τύποι εισιτηρίων.</p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        } />
        <Route path="/login" element={<Login setToken={setToken} />} />
        <Route path="/my-bookings" element={<MyBookings />} />
      </Routes>
    </Router>
  )
}

export default App