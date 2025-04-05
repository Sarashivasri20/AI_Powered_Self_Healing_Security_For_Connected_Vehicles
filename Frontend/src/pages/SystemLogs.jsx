import { useState, useEffect } from "react";
import axios from "axios";
import { Container, Table, Badge, Spinner } from "react-bootstrap";

function SystemLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/history?limit=10");
        setLogs(response.data.history || []);
      } catch (error) {
        console.error("Error fetching logs, using dummy data:", error);
        setLogs([
          {
            timestamp: "2025-04-02 12:00:00",
            vehicle_id: "V-12345",
            anomaly_score: 1,
            attack_type: "CAN Bus Flood Attack",
            gpt_explanation: "An unusually high number of CAN messages detected.",
            suggested_patch: "Apply message rate limiting on ECU."
          },
          {
            timestamp: "2025-04-02 11:45:00",
            vehicle_id: "V-67890",
            anomaly_score: 1,
            attack_type: "Normal Operation",
            gpt_explanation: "No significant anomalies detected.",
            suggested_patch: "No action required."
          }
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
    const interval = setInterval(fetchLogs, 10000); // Auto-refresh every 10 sec
    return () => clearInterval(interval);
  }, []);

  const getBadgeVariant = (anomalyScore) => {
    if (anomalyScore == 1) return "danger";
    return "success";                            // no anomaly
  };

  return (
    <Container className="system-logs-container mt-4">
      <h2 className="text-primary mb-3">📜 Threat Logs</h2>
      {loading ? (
        <Spinner animation="border" variant="primary" />
      ) : logs.length === 0 ? (
        <p className="text-muted">No recent threats detected.</p>
      ) : (
        <Table striped bordered hover responsive className="shadow-sm">
          <thead className="bg-dark text-white">
            <tr>
              <th>#</th>
              <th>Timestamp</th>
              <th>Vehicle ID</th>
              <th>Anomaly Score</th>
              <th>Attack Type</th>
              <th>GPT Explanation</th>
              <th>Suggested Patch</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{log.timestamp}</td>
                <td>{log.vehicle_id}</td>
                <td>
                  <Badge bg={getBadgeVariant(log.anomaly_score)}>
                    {log.anomaly_score}
                  </Badge>
                </td>
                <td>{log.attack}</td>
                <td>{log.gpt_explanation}</td>
                <td>{log.suggested_patch}</td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
}

export default SystemLogs;