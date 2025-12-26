import React, { useEffect, useState } from 'react';
import { getTasks, createTask } from '../services/api';
import { CheckCircle, Clock, Plus, AlertCircle } from 'lucide-react';

const TaskItem = ({ task }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
      case 'IN_PROGRESS': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      case 'PENDING': return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/20';
    }
  };

  const getPriorityColor = (priority) => {
      switch (priority) {
          case 'CRITICAL': return 'text-red-400';
          case 'HIGH': return 'text-orange-400';
          case 'MEDIUM': return 'text-blue-400';
          default: return 'text-slate-400';
      }
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-start gap-4">
      <div className={`mt-1 p-2 rounded-full ${getStatusColor(task.status)}`}>
        {task.status === 'COMPLETED' ? <CheckCircle size={18} /> : <Clock size={18} />}
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-start">
            <h4 className="text-white font-medium">{task.title}</h4>
            <span className={`text-xs font-mono px-2 py-0.5 rounded border border-slate-700 bg-slate-800 ${getPriorityColor(task.priority)}`}>
                {task.priority}
            </span>
        </div>
        <p className="text-slate-400 text-sm mt-1">{task.description}</p>
        <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
          <span>ID: {task.task_id.substring(0, 8)}...</span>
          <span>•</span>
          <span>Created by: {task.created_by}</span>
          {task.assigned_to && (
              <>
                <span>•</span>
                <span className="text-blue-400">Assigned: {task.assigned_to}</span>
              </>
          )}
        </div>
      </div>
    </div>
  );
};

const CreateTaskModal = ({ onClose, onCreated }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('MEDIUM');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createTask({ title, description, priority });
      onCreated();
      onClose();
    } catch (error) {
      console.error("Failed to create task", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full max-w-md shadow-2xl">
        <h3 className="text-xl font-bold text-white mb-4">Create New Task</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
              placeholder="e.g. Refactor API"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors h-24 resize-none"
              placeholder="Task details..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">Priority</label>
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white">Tasks</h2>
          <p className="text-slate-400 mt-2">Monitor and assign tasks</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <Plus size={18} />
          New Task
        </button>
      </div>

      {loading ? (
        <div className="text-slate-400">Loading tasks...</div>
      ) : tasks.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-slate-800 rounded-xl">
            <AlertCircle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No tasks found. Create one to get started.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tasks.map((task) => (
            <TaskItem key={task.task_id} task={task} />
          ))}
        </div>
      )}

      {isModalOpen && (
        <CreateTaskModal
          onClose={() => setIsModalOpen(false)}
          onCreated={fetchTasks}
        />
      )}
    </div>
  );
};

export default Tasks;
