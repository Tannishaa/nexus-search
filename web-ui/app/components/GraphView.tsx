"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

// Dynamically import the 3D library so it only loads in the browser (fixes "window is not defined" error)
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), { ssr: false });

export default function GraphView({ query, results, onClose }: { query: string, results: any[], onClose: () => void }) {
  
  // Convert our flat Search Results into a 3D Graph Structure (Nodes & Links)
  const graphData = useMemo(() => {
    const nodes = [];
    const links = [];

    // 1. The Central Node (The Search Query)
    nodes.push({ id: "ROOT", name: query, val: 20, color: "#a855f7" }); // Purple center

    // 2. The Result Nodes (The URLs)
    results.forEach((item, index) => {
      nodes.push({ 
        id: item.url, 
        name: item.title || item.url, 
        val: 10, 
        color: "#06b6d4", // Cyan nodes
        score: item.score || 1
      });
      
      // Link every result back to the center
      links.push({ source: "ROOT", target: item.url });
    });

    return { nodes, links };
  }, [query, results]);

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex flex-col">
      {/* Header / Close Button */}
      <div className="absolute top-0 left-0 right-0 p-6 flex justify-between items-center z-50 pointer-events-none">
        <div className="pointer-events-auto">
          <h2 className="text-white font-mono text-xl">
            <span className="text-purple-400">INDEX</span>_VISUALIZER
          </h2>
          <p className="text-zinc-500 text-xs mt-1">
            Visualizing {results.length} nodes for query "{query}"
          </p>
        </div>
        <button 
          onClick={onClose}
          className="pointer-events-auto bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-full font-mono text-xs border border-zinc-700 transition-all"
        >
          CLOSE_VIEW [ESC]
        </button>
      </div>

      {/* The 3D Canvas */}
      <div className="flex-1 w-full h-full cursor-move">
        <ForceGraph3D
          graphData={graphData}
          nodeLabel="name"
          nodeColor="color"
          nodeRelSize={6}
          linkColor={() => "#ffffff20"} // Faint white lines
          backgroundColor="#00000000" // Transparent
          showNavInfo={false}
          
          // Make it look cool (Bloom effect logic usually goes here, but we keep it simple)
          nodeResolution={16}
        />
      </div>
      
      {/* Instruction Overlay */}
      <div className="absolute bottom-8 left-0 right-0 text-center pointer-events-none">
        <p className="text-zinc-600 text-xs font-mono">
          DRAG TO ROTATE • SCROLL TO ZOOM • HOVER FOR DETAILS
        </p>
      </div>
    </div>
  );
}