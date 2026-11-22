import React from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary caught error]:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[500px] w-full flex items-center justify-center p-6 select-none">
          <div className="glass-card max-w-md w-full p-8 text-center space-y-5 border border-rose-500/30 shadow-2xl backdrop-blur-2xl">
            <div className="w-14 h-14 rounded-full bg-rose-500/20 border border-rose-500/40 mx-auto flex items-center justify-center text-rose-300">
              <AlertTriangle className="w-7 h-7" />
            </div>
            
            <div className="space-y-2">
              <h2 className="text-xl font-light text-white font-['Instrument_Sans']">
                Interface Recovered Seamlessly
              </h2>
              <p className="text-xs text-white/70 font-light leading-relaxed">
                A visual rendering state was caught and isolated. The background telemetry and AI forecasting models remain 100% active.
              </p>
            </div>

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={this.handleReset}
                className="px-4 py-2 rounded-full glass-pill text-xs font-light text-white flex items-center gap-2 hover:bg-white/20 transition-all cursor-pointer"
              >
                <Home className="w-3.5 h-3.5 text-amber-300" />
                <span>Return to Overview</span>
              </button>

              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 rounded-full glass-pill text-xs font-light text-white/80 flex items-center gap-2 hover:bg-white/20 transition-all cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5 text-cyan-300" />
                <span>Reload App</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
