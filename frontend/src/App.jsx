import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import CityDashboard from './pages/CityDashboard';
import HealthRiskPanel from './pages/HealthRiskPanel';
import AlertsFeed from './pages/AlertsFeed';
import AboutPage from './pages/AboutPage';
import { CITIES } from './data/mockData';
import { fetchLiveComparison, getCachedLiveComparison } from './data/api';
import { ThemeProvider } from './context/ThemeContext';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

function AppContent() {
  const [selectedCity, setSelectedCity] = useState(CITIES[0]);
  const [liveAQI, setLiveAQI] = useState(() => {
    const cached = getCachedLiveComparison(CITIES[0]);
    return cached?.live_actual?.value ?? null;
  });

  // Sync live AQI whenever selected city changes, plus continuous 60s background refresh
  useEffect(() => {
    let isMounted = true;
    const cached = getCachedLiveComparison(selectedCity);
    if (cached?.live_actual?.value != null) {
      setLiveAQI(cached.live_actual.value);
    }

    const loadLive = (bust = false) => {
      fetchLiveComparison(selectedCity, bust)
        .then((data) => {
          if (isMounted && data?.live_actual?.value != null) {
            setLiveAQI(data.live_actual.value);
          }
        })
        .catch(() => {});
    };

    loadLive(false);
    const interval = setInterval(() => loadLive(true), 60000);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [selectedCity]);

  return (
    <Router>
      {/* Outer neutral background wrapper */}
      <div className="min-h-screen p-2 sm:p-4 lg:p-6 flex flex-col items-center justify-center">
        
        {/* Master WeatherWise 32px rounded container */}
        <div className="weatherwise-container w-full max-w-[1400px] min-h-[92vh] flex flex-col relative">
          
          {/* Photographic Sky Background with fallback and subtle drift */}
          <div className="weatherwise-sky-bg ambient-drift" />
          
          {/* Subtle noise grain filter */}
          <div className="noise-overlay" />

          {/* Floating Navigation Header */}
          <Navbar 
            selectedCity={selectedCity} 
            onCityChange={setSelectedCity} 
            liveAQI={liveAQI}
          />

          {/* Main App Content Viewport */}
          <main className="relative z-10 flex-1 w-full pt-20 pb-8 px-4 sm:px-6 lg:px-8">
            <ErrorBoundary>
              <Routes>
                <Route path="/" element={<LandingPage onCityChange={setSelectedCity} />} />
                <Route
                  path="/dashboard"
                  element={
                    <CityDashboard 
                      city={selectedCity} 
                      onCityChange={setSelectedCity} 
                      onLiveAQIUpdate={setLiveAQI}
                    />
                  }
                />
                <Route
                  path="/risk"
                  element={<HealthRiskPanel city={selectedCity} onCityChange={setSelectedCity} liveAQI={liveAQI} />}
                />
                <Route
                  path="/alerts"
                  element={<AlertsFeed city={selectedCity} onCityChange={setSelectedCity} />}
                />
                <Route path="/about" element={<AboutPage />} />
              </Routes>
            </ErrorBoundary>
          </main>


        </div>

      </div>
    </Router>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
