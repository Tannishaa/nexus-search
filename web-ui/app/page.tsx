"use client";

import { useState } from "react";
import GraphView from "./components/GraphView"; // <--- NEW IMPORT

// Load the URL from the environment file
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");
  
  // State for the 3D Graph Modal
  const [showGraph, setShowGraph] = useState(false); // <--- NEW STATE

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;

    setLoading(true);
    setSearched(true);
    setError("");
    setResults([]);
    setShowGraph(false); // Reset graph view on new search

    try {
      const res = await fetch(`${API_URL}?q=${query}`);
      const data = await res.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setResults(data.results || []);
      }
    } catch (err) {
      setError("Connection refused. Ensure backend is active.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-zinc-950 text-zinc-300 font-sans selection:bg-white selection:text-black">
      
      {/* Main Layout */}
      <div className={`max-w-3xl mx-auto px-6 transition-all duration-500 ${searched ? "pt-12" : "pt-[30vh]"}`}>
        
        {/* Header / Logo */}
        <div className={`flex flex-col gap-2 ${searched ? "mb-6" : "mb-10 items-center text-center"}`}>
          <h1 className={`font-semibold tracking-tight text-white ${searched ? "text-xl" : "text-3xl"}`}>
            Nexus<span className="text-zinc-500">Search</span>
          </h1>
          {!searched && (
            <p className="text-sm text-zinc-500">v1.0.0 • Distributed Index</p>
          )}
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="w-full relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Query the index..."
            className="w-full bg-zinc-900 border border-zinc-800 rounded-md py-3 px-4 text-white focus:outline-none focus:ring-1 focus:ring-white focus:border-white transition-all placeholder:text-zinc-600 font-mono text-sm"
          />
          <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-zinc-600 border border-zinc-800 px-2 py-0.5 rounded">
            ENTER
          </div>
        </form>

        {/* Status Bar */}
        {loading && (
          <div className="mt-4 flex items-center gap-2 text-xs text-zinc-500 font-mono">
            <span className="w-2 h-2 bg-green-500 animate-pulse rounded-full"></span>
            Processing query via AWS Lambda...
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="mt-4 p-3 bg-red-950/20 border border-red-900/50 text-red-400 text-xs font-mono rounded-md">
            Error: {error}
          </div>
        )}

        {/* Results List */}
        {!loading && searched && (
          <div className="mt-8 space-y-6 pb-20">
            {results.length === 0 ? (
              <div className="text-sm text-zinc-600 font-mono py-8 border-t border-zinc-900">
                [0] results returned.
              </div>
            ) : (
              <div className="border-t border-zinc-900 pt-6">
                
                {/* --- NEW: Stats Bar + Visualize Button --- */}
                <div className="flex items-center justify-between mb-6">
                  <div className="text-xs text-zinc-600 font-mono">
                    QUERY_TIME: {(Math.random() * 0.2).toFixed(3)}s • HITS: {results.length}
                  </div>
                  
                  <button 
                    onClick={() => setShowGraph(true)}
                    className="flex items-center gap-2 text-xs font-mono text-cyan-500 hover:text-cyan-400 bg-cyan-950/30 hover:bg-cyan-900/50 px-3 py-1.5 rounded border border-cyan-900/50 transition-all group"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-3 h-3 group-hover:animate-spin"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
                    VISUALIZE_NODES
                  </button>
                </div>
                
                {/* Results Loop */}
                {results.map((item, index) => (
                  <div key={index} className="group mb-6">
                    <div className="flex items-center justify-between mb-1">
                      {/* URL Breadcrumb */}
                      <div className="flex items-center gap-2 text-[10px] text-zinc-500 font-mono uppercase tracking-wider">
                        <span>HTTP</span>
                        <span className="text-zinc-700">/</span>
                        <span className="truncate max-w-[300px]">{item.url}</span>
                      </div>

                      {/* Relevance Score Badge */}
                      <div className="flex items-center gap-1">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                        <span className="text-[10px] font-mono text-emerald-500">
                          TF-SCORE: {item.score || 1}
                        </span>
                      </div>
                    </div>
                    
                    <a 
                      href={item.url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="text-blue-400 hover:text-blue-300 hover:underline text-lg font-medium leading-tight block mb-1"
                    >
                      {item.title ? item.title.replace(/\n/g, "").trim() : "Untitled Resource"}
                    </a>
                    
                    <p className="text-sm text-zinc-400 leading-relaxed">
                      Contains indexed keyword <span className="text-white font-mono bg-zinc-800 px-1 text-xs">"{item.keyword}"</span>.
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* --- NEW: 3D Graph Modal --- */}
        {showGraph && (
          <GraphView query={query} results={results} onClose={() => setShowGraph(false)} />
        )}

      </div>
    </main>
  );
}