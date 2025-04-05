import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

function Header() {
  return (
    <Container fluid className="app-container p-0">
      <Navbar className="bg-body-tertiary mb-3 rounded shadow-sm p-3 w-100">
        <Container>
          <Navbar.Brand href="/" className="fw-bold text-primary">
            FleetGuard
          </Navbar.Brand>
          <Navbar.Toggle />
          <Nav className="me-auto">
            <Nav.Link href="/">Dashboard</Nav.Link>  {/* 🚗 Live vehicle status */}
            <Nav.Link href="/threats">Threat Alerts</Nav.Link>  {/* 🚨 Alerts page */}
            <Nav.Link href="/logs">System Logs</Nav.Link>  {/* 📜 History of attacks */}
            <Nav.Link href="/voice">Voice Control</Nav.Link>  {/* 🎙️ Whisper AI */}
          </Nav>
          <Navbar.Collapse className="justify-content-end">
            <Navbar.Text>
              Signed in as: <a href='/me'>Krishnendu M R</a>
            </Navbar.Text>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </Container>
  );
}

export default Header;
