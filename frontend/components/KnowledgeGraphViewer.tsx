'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { GraphResponse, GraphNode, GraphEdge } from '@/lib/types';
import { Network, ZoomIn, ZoomOut, RotateCcw, Info, ArrowRight, Layers, ShieldCheck, Clock } from 'lucide-react';

interface KnowledgeGraphViewerProps {
  graph: GraphResponse;
  height?: string;
  centralEventId?: string;
}

export default function KnowledgeGraphViewer({
  graph,
  height = '600px',
  centralEventId,
}: KnowledgeGraphViewerProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(centralEventId || null);
  const [zoom, setZoom] = useState<number>(1);
  const [filterType, setFilterType] = useState<'ALL' | 'EVENTS' | 'ENTITIES'>('ALL');

  // Compute positions using deterministic radial / circular layout for clarity and stability
  const layout = useMemo(() => {
    const width = 800;
    const h = 600;
    const centerX = width / 2;
    const centerY = h / 2;

    const visibleNodes = graph.nodes.filter(n => {
      if (filterType === 'EVENTS') return n.type === 'EVENT';
      if (filterType === 'ENTITIES') return n.type === 'ENTITY';
      return true;
    });

    const nodeMap = new Map<string, { node: GraphNode; x: number; y: number }>();

    // If central event exists, place it in center
    const central = visibleNodes.find(n => n.id === centralEventId || n.is_central);
    const others = visibleNodes.filter(n => n !== central);

    if (central) {
      nodeMap.set(central.id, { node: central, x: centerX, y: centerY });
    }

    // Split others into event ring (inner) and entity ring (outer)
    const eventOthers = others.filter(n => n.type === 'EVENT');
    const entityOthers = others.filter(n => n.type === 'ENTITY');

    const innerRadius = central ? 180 : 160;
    const outerRadius = 260;

    eventOthers.forEach((n, idx) => {
      const angle = (idx / Math.max(eventOthers.length, 1)) * 2 * Math.PI - Math.PI / 2;
      nodeMap.set(n.id, {
        node: n,
        x: centerX + innerRadius * Math.cos(angle),
        y: centerY + innerRadius * Math.sin(angle),
      });
    });

    entityOthers.forEach((n, idx) => {
      const angle = (idx / Math.max(entityOthers.length, 1)) * 2 * Math.PI - Math.PI / 4;
      nodeMap.set(n.id, {
        node: n,
        x: centerX + outerRadius * Math.cos(angle),
        y: centerY + outerRadius * Math.sin(angle),
      });
    });

    // Edges between visible nodes
    const visibleEdges = graph.edges.filter(
      e => nodeMap.has(e.source) && nodeMap.has(e.target)
    );

    return { width, height: h, nodes: Array.from(nodeMap.values()), edges: visibleEdges, nodeMap };
  }, [graph, filterType, centralEventId]);

  const selectedNode = useMemo(() => {
    return graph.nodes.find(n => n.id === selectedNodeId) || null;
  }, [graph.nodes, selectedNodeId]);

  // Connected edges for the selected node
  const connectedEdges = useMemo(() => {
    if (!selectedNodeId) return [];
    return graph.edges.filter(
      e => e.source === selectedNodeId || e.target === selectedNodeId
    );
  }, [graph.edges, selectedNodeId]);

  const getNodeColor = (node: GraphNode) => {
    if (node.type === 'ENTITY') return 'fill-amber-50 stroke-amber-400 text-amber-900';
    switch (node.category) {
      case 'Parliament':
        return 'fill-indigo-50 stroke-indigo-400 text-indigo-900';
      case 'Defence':
        return 'fill-red-50 stroke-red-400 text-red-900';
      case 'Economics':
        return 'fill-emerald-50 stroke-emerald-400 text-emerald-900';
      case 'Trade':
        return 'fill-cyan-50 stroke-cyan-400 text-cyan-900';
      case 'Geopolitics':
        return 'fill-purple-50 stroke-purple-400 text-purple-900';
      default:
        return 'fill-slate-50 stroke-slate-400 text-slate-900';
    }
  };

  const getEdgeStyle = (type: string) => {
    switch (type) {
      case 'CAUSES':
        return { stroke: '#dc2626', strokeWidth: 2.5, strokeDasharray: undefined };
      case 'PRECEDES':
        return { stroke: '#2563eb', strokeWidth: 2, strokeDasharray: undefined };
      case 'RELATED_TO':
        return { stroke: '#059669', strokeWidth: 1.8, strokeDasharray: '4 3' };
      default:
        return { stroke: '#94a3b8', strokeWidth: 1.2, strokeDasharray: '2 2' };
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm flex flex-col">
      {/* Top Toolbar */}
      <div className="px-5 py-3 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 bg-slate-50/70">
        <div className="flex items-center space-x-2 text-sm font-semibold text-slate-800">
          <Network className="w-4 h-4 text-blue-600" />
          <span>Knowledge Network Projection</span>
          <span className="text-xs font-normal text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
            {graph.node_count} nodes · {graph.edge_count} edges
          </span>
        </div>

        {/* Filter & Zoom Controls */}
        <div className="flex items-center space-x-3">
          <div className="inline-flex rounded-lg border border-slate-200 bg-white p-0.5 text-xs font-medium">
            <button
              onClick={() => setFilterType('ALL')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterType === 'ALL' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('EVENTS')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterType === 'EVENTS' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Events
            </button>
            <button
              onClick={() => setFilterType('ENTITIES')}
              className={`px-2.5 py-1 rounded-md transition-colors ${
                filterType === 'ENTITIES' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Entities
            </button>
          </div>

          <div className="flex items-center space-x-1 border border-slate-200 rounded-lg bg-white p-0.5">
            <button
              onClick={() => setZoom(z => Math.max(z - 0.15, 0.5))}
              className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded"
              title="Zoom out"
              aria-label="Zoom out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoom(1)}
              className="px-1.5 py-0.5 text-xs font-medium text-slate-600 hover:bg-slate-100 rounded"
              title="Reset Zoom"
            >
              {Math.round(zoom * 100)}%
            </button>
            <button
              onClick={() => setZoom(z => Math.min(z + 0.15, 2.0))}
              className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded"
              title="Zoom in"
              aria-label="Zoom in"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Graph Canvas & Inspector */}
      <div className="relative flex flex-col md:flex-row" style={{ height }}>
        {/* SVG Viewport */}
        <div className="flex-1 overflow-hidden bg-slate-950/[0.02] relative cursor-grab active:cursor-grabbing">
          {graph.node_count === 0 ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400 p-8 text-center">
              <Layers className="w-10 h-10 mb-2 stroke-1 text-slate-300" />
              <p className="text-sm font-medium">No graph relationships found for this scope.</p>
              <p className="text-xs text-slate-400 mt-1">Relationships are inferred automatically as events are verified.</p>
            </div>
          ) : (
            <svg
              className="w-full h-full"
              viewBox={`0 0 ${layout.width} ${layout.height}`}
              style={{
                transform: `scale(${zoom})`,
                transformOrigin: 'center center',
                transition: 'transform 0.15s ease-out',
              }}
            >
              <defs>
                <marker
                  id="arrow-default"
                  viewBox="0 0 10 10"
                  refX="22"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8" />
                </marker>
                <marker
                  id="arrow-causes"
                  viewBox="0 0 10 10"
                  refX="22"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#dc2626" />
                </marker>
                <marker
                  id="arrow-precedes"
                  viewBox="0 0 10 10"
                  refX="22"
                  refY="5"
                  markerWidth="6"
                  markerHeight="6"
                  orient="auto-start-reverse"
                >
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#2563eb" />
                </marker>
              </defs>

              {/* Edges */}
              {layout.edges.map(edge => {
                const s = layout.nodeMap.get(edge.source);
                const t = layout.nodeMap.get(edge.target);
                if (!s || !t) return null;

                const isHighlighted =
                  selectedNodeId && (edge.source === selectedNodeId || edge.target === selectedNodeId);
                const edgeStyle = getEdgeStyle(edge.type);

                const marker =
                  edge.type === 'CAUSES'
                    ? 'url(#arrow-causes)'
                    : edge.type === 'PRECEDES'
                    ? 'url(#arrow-precedes)'
                    : 'url(#arrow-default)';

                const midX = (s.x + t.x) / 2;
                const midY = (s.y + t.y) / 2;

                return (
                  <g key={edge.id} className="transition-opacity duration-200">
                    <line
                      x1={s.x}
                      y1={s.y}
                      x2={t.x}
                      y2={t.y}
                      stroke={edgeStyle.stroke}
                      strokeWidth={isHighlighted ? edgeStyle.strokeWidth + 1 : edgeStyle.strokeWidth}
                      strokeDasharray={edgeStyle.strokeDasharray}
                      opacity={selectedNodeId ? (isHighlighted ? 1 : 0.2) : 0.75}
                      markerEnd={marker}
                    />
                    {/* Relationship label */}
                    {(isHighlighted || edge.type === 'CAUSES' || edge.type === 'PRECEDES') && (
                      <text
                        x={midX}
                        y={midY - 4}
                        fill={edgeStyle.stroke}
                        fontSize="9"
                        fontWeight="600"
                        textAnchor="middle"
                        className="pointer-events-none select-none bg-white"
                      >
                        {edge.type}
                      </text>
                    )}
                  </g>
                );
              })}

              {/* Nodes */}
              {layout.nodes.map(({ node, x, y }) => {
                const isSelected = node.id === selectedNodeId;
                const isCentral = node.is_central || node.id === centralEventId;
                const colorClass = getNodeColor(node);

                return (
                  <g
                    key={node.id}
                    transform={`translate(${x}, ${y})`}
                    onClick={() => setSelectedNodeId(node.id)}
                    className="cursor-pointer group"
                  >
                    {node.type === 'EVENT' ? (
                      // Event Node: Rounded Card Pill
                      <>
                        <rect
                          x="-65"
                          y="-20"
                          width="130"
                          height="40"
                          rx="8"
                          className={`${colorClass} transition-all duration-150 ${
                            isSelected
                              ? 'stroke-2 stroke-blue-600 filter drop-shadow-md'
                              : isCentral
                              ? 'stroke-2 stroke-slate-900'
                              : 'stroke-1'
                          }`}
                        />
                        <text
                          x="0"
                          y="-2"
                          textAnchor="middle"
                          fontSize="10"
                          fontWeight={isSelected || isCentral ? '700' : '600'}
                          fill="#0f172a"
                          className="select-none pointer-events-none"
                        >
                          {node.label.length > 20 ? `${node.label.slice(0, 18)}…` : node.label}
                        </text>
                        <text
                          x="0"
                          y="11"
                          textAnchor="middle"
                          fontSize="8"
                          fontWeight="500"
                          fill="#64748b"
                          className="select-none pointer-events-none uppercase tracking-wider"
                        >
                          {node.category || 'Event'}
                        </text>
                      </>
                    ) : (
                      // Entity Node: Rounded Circle
                      <>
                        <circle
                          r={isSelected ? '22' : '18'}
                          className={`${colorClass} transition-all duration-150 ${
                            isSelected ? 'stroke-2 stroke-amber-600 filter drop-shadow-md' : 'stroke-1'
                          }`}
                        />
                        <text
                          x="0"
                          y="3"
                          textAnchor="middle"
                          fontSize="9"
                          fontWeight="600"
                          fill="#78350f"
                          className="select-none pointer-events-none"
                        >
                          {node.label.length > 10 ? `${node.label.slice(0, 8)}…` : node.label}
                        </text>
                      </>
                    )}
                  </g>
                );
              })}
            </svg>
          )}

          {/* Graph Legend */}
          <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm border border-slate-200 rounded-lg p-2.5 shadow-sm text-xs space-y-1.5 pointer-events-auto">
            <div className="font-semibold text-slate-700 text-[11px] mb-1">Relationship Inferences</div>
            <div className="flex items-center space-x-2 text-slate-600">
              <span className="w-3 h-0.5 bg-red-600 inline-block"></span>
              <span><strong>CAUSES</strong> (Semantic &ge; 0.85, Overlap &ge; 0.6)</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600">
              <span className="w-3 h-0.5 bg-blue-600 inline-block"></span>
              <span><strong>PRECEDES</strong> (Temporal sequence in Story)</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600">
              <span className="w-3 h-0.5 border-b border-dashed border-emerald-600 inline-block"></span>
              <span><strong>RELATED_TO</strong> (Shared Entities &ge; 3)</span>
            </div>
          </div>
        </div>

        {/* Node Inspector Drawer */}
        {selectedNode && (
          <div className="w-full md:w-80 border-t md:border-t-0 md:border-l border-slate-200 bg-white p-5 overflow-y-auto space-y-4 flex-shrink-0">
            <div className="flex items-start justify-between">
              <div>
                <span
                  className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                    selectedNode.type === 'EVENT'
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  {selectedNode.type}
                </span>
                <span className="ml-2 text-xs text-slate-500 font-medium">
                  {selectedNode.category}
                </span>
              </div>
              {selectedNode.status && (
                <span className="inline-flex items-center text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  {selectedNode.status}
                </span>
              )}
            </div>

            <div>
              <h3 className="text-base font-semibold text-slate-900 leading-snug">
                {selectedNode.label}
              </h3>
            </div>

            {selectedNode.type === 'EVENT' && (
              <div className="pt-2">
                <Link
                  href={`/events/${selectedNode.id}`}
                  className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <span>Open Event Dossier</span>
                  <ArrowRight className="w-3.5 h-3.5 ml-1" />
                </Link>
              </div>
            )}

            {/* Connected Edges Summary */}
            <div className="pt-3 border-t border-slate-100">
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Connected Relationships ({connectedEdges.length})
              </h4>
              {connectedEdges.length === 0 ? (
                <p className="text-xs text-slate-400">No active relationship edges recorded.</p>
              ) : (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {connectedEdges.map(edge => {
                    const otherId = edge.source === selectedNode.id ? edge.target : edge.source;
                    const otherNode = graph.nodes.find(n => n.id === otherId);
                    const isOutgoing = edge.source === selectedNode.id;

                    return (
                      <div
                        key={edge.id}
                        className="p-2 bg-slate-50 border border-slate-100 rounded text-xs space-y-1"
                      >
                        <div className="flex items-center justify-between font-medium">
                          <span className="text-slate-800">
                            {isOutgoing ? '→' : '←'} {edge.type}
                          </span>
                          <span className="text-[10px] text-slate-500 font-mono">
                            {Math.round(edge.confidence * 100)}% conf
                          </span>
                        </div>
                        <div className="text-slate-600 truncate">
                          {otherNode ? otherNode.label : otherId}
                        </div>
                        {edge.reasoning && (
                          <div className="text-[10px] text-slate-400 italic">
                            {edge.reasoning}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
