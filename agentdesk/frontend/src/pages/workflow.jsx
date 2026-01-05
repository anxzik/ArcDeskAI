import React, { useState, useCallback } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  MiniMap,
  applyEdgeChanges,
  applyNodeChanges
} from 'reactflow';
import 'reactflow/dist/style.css';
import Layout from '@/components/Layout';

const initialNodes = [
  {
    id: '1',
    type: 'input',
    data: { label: 'Input Agent' },
    position: { x: 250, y: 25 },
  },
  {
    id: '2',
    data: { label: 'Processing Agent' },
    position: { x: 100, y: 125 },
  },
  {
    id: '3',
    data: { label: 'Output Agent' },
    position: { x: 400, y: 125 },
  },
];

const initialEdges = [{ id: 'e1-2', source: '1', target: '2' }];

const WorkflowPage = () => {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => addEdge(changes, eds)),
    []
  );

  return (
    <Layout>
      <div className="flex flex-col h-[calc(100-120px)] min-h-[600px]">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Workflow Planner</h2>
          <div className="space-x-2">
            <button className="px-4 py-2 bg-blue-600 rounded text-sm hover:bg-blue-700">Save Workflow</button>
            <button className="px-4 py-2 bg-slate-700 rounded text-sm hover:bg-slate-600">Deploy Team</button>
          </div>
        </div>
        
        <div className="flex-grow bg-slate-800 rounded-lg border border-slate-700 relative overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="#334155" gap={20} />
            <Controls />
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'input') return '#3b82f6';
                return '#94a3b8';
              }}
              maskColor="rgba(15, 23, 42, 0.6)"
            />
          </ReactFlow>
        </div>
      </div>
    </Layout>
  );
};

export default WorkflowPage;
