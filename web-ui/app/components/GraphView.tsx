"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

// Dynamically import the 3D library so it only loads in the browser
const ForceGraph3D = dynamic(() => import("react-force-graph-3d"), { ssr: false });

// 1. Define types for our data to satisfy TypeScript
interface GraphNode {
  id: string;
  name: string;
  val: number;
  color: string;
  score?: number;
}

interface GraphLink {
  source: string;
  target: string;
}

export default function GraphView({ query, results, onClose }: { query: string, results: any[], onClose: () => void }) {
  
  const graphData = useMemo(() => {
    // 2. Explicitly tell TypeScript these arrays will hold our specific types
    const nodes: GraphNode[] = [];
    const links: GraphLink[] = [];

    // Central Node (The Search Query)
    nodes.push({ id: "ROOT", name: query, val: 20, color: "#a855f7" }); 

    // Result Nodes (The URLs)
    results.forEach((item) => {
      nodes.push({ 
        id: item.url, 
        name: item.title || item.url, 
        val: 10, 
        color: "#06b6d4",
        score: item.score || 1
      });
      
      links.push({ source: "ROOT", target: item.url });
    });

    return { nodes, links };
  }, [query, results]);

  return (
    <div className="fixed inset-0 z-50 bg-black/90 flex flex-col">
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

      <div className="flex-1 w-full h-full cursor-move">
        <ForceGraph3D
          graphData={graphData}
          nodeLabel="name"
          nodeColor="color"
          nodeRelSize={6}
          linkColor={() => "#ffffff20"}
          backgroundColor="#00000000"
          showNavInfo={false}
          nodeResolution={16}
        />
      </div>
      
      <div className="absolute bottom-8 left-0 right-0 text-center pointer-events-none">
        <p className="text-zinc-600 text-xs font-mono">
          DRAG TO ROTATE • SCROLL TO ZOOM • HOVER FOR DETAILS
        </p>
      </div>
    </div>
  );
}