import { useState, useEffect } from "react";
import { Container, Table, Button, Modal } from "react-bootstrap";
import axios from "axios";

function ThreatAlerts() {
  const [threats, setThreats] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [selectedFix, setSelectedFix] = useState("");
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [applyResult, setApplyResult] = useState("");

  useEffect(() => {
    const fetchThreats = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/threat?limit=10");
        console.log("Fetched Threats:", response.data);
        const filteredThreats = response.data.history;
        setThreats(filteredThreats);
      } catch (error) {
        console.error("Error fetching threat history:", error);
        // Fallback dummy data if backend fails
        setThreats([
          {
            id: 1,
            timestamp: "2025-04-02 12:00:00",
            attack: "ECU Tampering",
            suggested_patch: "Update ECU firmware immediately.",
          },
          {
            id: 2,
            timestamp: "2025-04-02 12:05:00",
            attack: "CAN Bus Flood Attack",
            suggested_patch: "Limit message rate from unknown sources.",
          },
          {
            id: 3,
            timestamp: "2025-04-02 12:10:00",
            attack: "Unauthorized Access",
            suggested_patch: "Change system access credentials.",
          },
        ]);
      }
    };

    fetchThreats();
    const interval = setInterval(fetchThreats, 8000);
    return () => clearInterval(interval);
  }, []);

  const speakText = async (text) => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/tts",
        { text },
        { responseType: "blob" }
      );
      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error generating speech:", error);
    }
  };

  const handleSuggestFix = (patch) => {
    setSelectedFix(patch);
    setShowModal(true);
    speakText(patch);
  };

  const handleApplyFix = async (patch) => {
    try {
      const response = await axios.post("http://127.0.0.1:5000/apply_patch", { patch });
      setApplyResult(response.data.status + response.data.patch_applied || "Patch applied successfully!");
    } catch (error) {
      console.error("Error applying patch:", error);
      setApplyResult("Failed to apply patch. Please try again.");
    }
    setShowApplyModal(true);
  };

  return (
    <Container className="threat-alerts-container">
      <h2 className="text-danger mb-3">🚨 Threat Alerts</h2>
      {threats.length === 0 ? (
        <p className="text-muted">No threats detected. System is secure. ✅</p>
      ) : (
        <Table striped bordered hover responsive className="shadow-sm">
          <thead className="bg-dark text-white">
            <tr>
              <th>#</th>
              <th>Timestamp</th>
              <th>Threat Type</th>
              <th>Suggestion</th>
              <th>Fix</th>
            </tr>
          </thead>
          <tbody>
            {threats.map((threat, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{threat.timestamp}</td>
                <td>{threat.attack || "Unknown"}</td>
                <td>
                  <Button
                    variant="warning"
                    size="sm"
                    className="me-2"
                    onClick={() =>
                      handleSuggestFix(threat.suggested_patch || "No fix available")
                    }
                  >
                    💡 Suggest Fix
                  </Button>
                </td>
                <td>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={() =>
                      handleApplyFix(threat.suggested_patch || "No fix available")
                    }
                  >
                    ✅ Apply Fix
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Suggest Fix Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>💡 Suggested Fix</Modal.Title>
        </Modal.Header>
        <Modal.Body>{selectedFix}</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Apply Fix Result Modal */}
      <Modal show={showApplyModal} onHide={() => setShowApplyModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>✅ Apply Fix Result</Modal.Title>
        </Modal.Header>
        <Modal.Body>{applyResult}</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowApplyModal(false)}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}

export default ThreatAlerts;
