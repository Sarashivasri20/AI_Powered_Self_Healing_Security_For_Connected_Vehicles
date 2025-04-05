import { StrictMode, useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import "bootstrap/dist/css/bootstrap.min.css";
import { Suspense, lazy } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import axios from "axios"; 
import Header from "./components/Header.jsx";
import ScreenLoader from "./components/ScreenLoader.jsx";
import Loading from "./components/Loading.jsx";
import "./index.css";
import AOS from 'aos';
import 'aos/dist/aos.css'; 

AOS.init();


const Dashboard = lazy(() => import("./pages/Dashboard.jsx"));
const ThreatAlerts = lazy(() => import("./pages/ThreatAlerts.jsx"));
const SystemLogs = lazy(() => import("./pages/SystemLogs.jsx"));
const VoiceControl = lazy(() => import("./pages/VoiceControl.jsx"));
const Profile = lazy(() => import("./pages/Profile.jsx"));

function Main() {
  const [loading, setLoading] = useState(true);
  const [vehicleData, setVehicleData] = useState(null);
  const [detectionResult, setDetectionResult] = useState(null);
  const [backendAvailable, setBackendAvailable] = useState(true);

  useEffect(() => {
    AOS.init({
      duration: 1000, // animation duration in ms
      once: true      // animate only once when scrolled into view
    });
  }, []);
  
  useEffect(() => {
    AOS.refresh(); // 👈 this ensures AOS recalculates animations on new content
  });
  

  useEffect(() => {
    const fetchVehicleData = async () => {
      try {
        const response = await axios.get("http://127.0.0.1:5000/vehicle_data");
        setVehicleData({ ...response.data });
        setBackendAvailable(true);
      } catch {
        setBackendAvailable(false);
        setVehicleData((prev) => prev || generateDummyData());
      }
    };

    fetchVehicleData();
    const interval = setInterval(fetchVehicleData, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const detectAnomaly = async () => {
      if (!vehicleData || !backendAvailable) return;
      try {
        const response = await axios.post("http://127.0.0.1:5000/detect", vehicleData);
        setDetectionResult(response.data);
      } catch (error) {
        console.error("Auto detection error:", error);
      }
    };

    detectAnomaly();
    const interval = setInterval(detectAnomaly, 20000);
    return () => clearInterval(interval);
  }, [vehicleData, backendAvailable]);

  const generateDummyData = () => ({
    byte_0: 2800,
    byte_1: 45,
    byte_2: 120,
    byte_3: 2,
    byte_4: 62,
    byte_5: 68,
    byte_6: 12.5,
    byte_7: 3,
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  return (
    <StrictMode>
      {loading ? (
        <ScreenLoader />
      ) : (
        <Router>
          <Header />
          <Suspense fallback={<Loading />}>
            <Routes>
              <Route path="/" element={<Dashboard vehicleData={vehicleData} detectionResult={detectionResult} />} />
              <Route path="/threats" element={<ThreatAlerts />} />
              <Route path="/logs" element={<SystemLogs />} />
              <Route path="/voice" element={<VoiceControl />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </Suspense>
        </Router>
      )}
    </StrictMode>
  );
}

createRoot(document.getElementById("root")).render(<Main />);
