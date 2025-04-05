import {
  Container,
  Row,
  Col,
  Card,
  Badge,
  Button,
  Spinner,
  Alert,
  Modal,
} from "react-bootstrap";
import {
  FaTachometerAlt,
  FaCarBattery,
  FaExclamationTriangle,
  FaShieldAlt,
  FaSearch,
} from "react-icons/fa";
import "../styles/Dashboard.css"; // ensure styles have custom card CSS

function Dashboard({ vehicleData, detectionResult }) {
  if (!vehicleData) {
    return <p className="text-center text-muted">Loading vehicle data...</p>;
  }

  const isThreatDetected = detectionResult?.result === "anomaly";

  return (
    <Container className="dashboard-container py-4 realtive">
      <h2 className="text-center text-gradient mb-5">⚙️ Vehicle Security Dashboard</h2>

      <Row className="gy-4">
        <Col md={3}>
          <Card className="dashboard-card shadow-md h-100 glass-effect">
            <Card.Body className="text-center">
              <FaTachometerAlt size={40} className="mb-3 text-info" />
              <Card.Title className="fw-bold">Speed & RPM</Card.Title>
              <Card.Text>🚗 Speed: {vehicleData.byte_4} km/h</Card.Text>
              <Card.Text>🔁 RPM: {vehicleData.byte_0}</Card.Text>
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card className={`dashboard-card shadow-md text-center h-100 pulse-card ${isThreatDetected ? "border-danger threat-flash" : "border-success"}`}>
            <Card.Body>
              {isThreatDetected ? (
                <>
                  <FaExclamationTriangle size={50} className="mb-3 text-danger" />
                  <Card.Title className="text-danger fw-bold">🚨 Threat Detected!</Card.Title>
                  <Card.Text className="mb-2">{detectionResult?.gpt_explanation || "Potential Attack Detected!"}</Card.Text>
                  <Badge bg="danger" className="gradient-badge px-3 py-2 rounded-pill">
                    {detectionResult?.suggested_patch || "Apply Patch"}
                  </Badge>
                </>
              ) : (
                <>
                  <FaShieldAlt size={50} className="mb-3 text-success" />
                  <Card.Title className="text-success fw-bold">✅ System Secure</Card.Title>
                  <Badge bg="success" className="gradient-badge px-3 py-2 rounded-pill">No Threats</Badge>
                </>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={3}>
          <Card className="dashboard-card shadow-md h-100 glass-effect">
            <Card.Body className="text-center">
              <FaCarBattery size={40} className="mb-3 text-success" />
              <Card.Title className="fw-bold">Battery & Throttle</Card.Title>
              <Card.Text>🔋 Battery: {vehicleData.byte_6}V</Card.Text>
              <Card.Text>⚡ Throttle: {vehicleData.byte_1}%</Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Dashboard;
