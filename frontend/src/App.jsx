import React, { useState, useEffect, useCallback } from 'react';

const STATUSES = ['New', 'In Process', 'Deferred', 'Complete'];

const STATUS_COLORS = {
  'New': '#3b82f6',
  'In Process': '#f59e0b',
  'Deferred': '#6b7280',
  'Complete': '#10b981',
};

const PRIORITY_LABELS = {
  1: 'P1', 2: 'P2', 3: 'P3', 4: 'P4', 5: 'P5',
  6: 'P6', 7: 'P7', 8: 'P8', 9: 'P9', 10: 'P10',
};

const PRIORITY_COLORS = (p) => {
  if (p <= 3) return '#ef4444';
  if (p <= 6) return '#f59e0b';
  return '#10b981';
};

const emptyForm = {
  title: '',
  description: '',
  due_date: '',
  priority: 5,
  status: 'New',
};

export default function App() {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingTodo, setEditingTodo] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [formErrors, setFormErrors] = useState({});
  const [filterStatus, setFilterStatus] = useState('');
  const [filterPriority, setFilterPriority] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [deleteConfirmId, setDeleteConfirmId] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterPriority) params.append('priority', filterPriority);
      params.append('sort_by', sortBy);
      params.append('sort_order', sortOrder);
      const res = await fetch(`/api/todos?${params.toString()}`);
      if (!res.ok) throw new Error(`Failed to fetch todos: ${res.statusText}`);
      const data = await res.json();
      setTodos(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [filterStatus, filterPriority, sortBy, sortOrder]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const showSuccess = (msg) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(''), 3000);
  };

  const validateForm = () => {
    const errs = {};
    if (!form.title.trim()) errs.title = 'Title is required';
    if (form.title.length > 200) errs.title = 'Title must be 200 chars or less';
    if (form.priority < 1 || form.priority > 10) errs.priority = 'Priority must be 1–10';
    if (!STATUSES.includes(form.status)) errs.status = 'Invalid status';
    return errs;
  };

  const openAddModal = () => {
    setEditingTodo(null);
    setForm(emptyForm);
    setFormErrors({});
    setShowModal(true);
  };

  const openEditModal = (todo) => {
    setEditingTodo(todo);
    setForm({
      title: todo.title,
      description: todo.description || '',
      due_date: todo.due_date || '',
      priority: todo.priority,
      status: todo.status,
    });
    setFormErrors({});
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTodo(null);
    setForm(emptyForm);
    setFormErrors({});
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: name === 'priority' ? parseInt(value, 10) : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = validateForm();
    if (Object.keys(errs).length > 0) {
      setFormErrors(errs);
      return;
    }
    setFormErrors({});
    const payload = {
      title: form.title.trim(),
      description: form.description.trim(),
      due_date: form.due_date || null,
      priority: form.priority,
      status: form.status,
    };
    try {
      if (editingTodo) {
        const res = await fetch(`/api/todos/${editingTodo.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to update todo');
        }
        showSuccess('Todo updated successfully!');
      } else {
        const res = await fetch('/api/todos', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        if (!res.ok) {
          const err = await res.json();
          throw new Error(err.detail || 'Failed to create todo');
        }
        showSuccess('Todo created successfully!');
      }
      closeModal();
      fetchTodos();
    } catch (e) {
      setFormErrors({ submit: e.message });
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await fetch(`/api/todos/${id}`, { method: 'DELETE' });
      if (!res.ok && res.status !== 204) throw new Error('Failed to delete todo');
      setDeleteConfirmId(null);
      showSuccess('Todo deleted.');
      fetchTodos();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleStatusChange = async (todo, newStatus) => {
    try {
      const res = await fetch(`/api/todos/${todo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error('Failed to update status');
      fetchTodos();
    } catch (e) {
      setError(e.message);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    const [year, month, day] = dateStr.split('-');
    return `${month}/${day}/${year}`;
  };

  const today = new Date().toISOString().split('T')[0];

  const stats = {
    total: todos.length,
    new: todos.filter(t => t.status === 'New').length,
    inProcess: todos.filter(t => t.status === 'In Process').length,
    deferred: todos.filter(t => t.status === 'Deferred').length,
    complete: todos.filter(t => t.status === 'Complete').length,
    overdue: todos.filter(t => t.is_overdue).length,
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <span className="logo">✅</span>
            <h1 className="app-title">TodoFlow</h1>
          </div>
          <button className="btn btn-primary btn-add" onClick={openAddModal}>
            <span className="btn-icon">+</span> New Todo
          </button>
        </div>
      </header>

      <main className="main">
        {successMsg && (
          <div className="alert alert-success">{successMsg}</div>
        )}
        {error && (
          <div className="alert alert-error">
            {error}
            <button className="alert-close" onClick={() => setError(null)}>×</button>
          </div>
        )}

        <div className="stats-bar">
          <div className="stat-chip stat-total"><span className="stat-num">{stats.total}</span> Total</div>
          <div className="stat-chip stat-new"><span className="stat-num">{stats.new}</span> New</div>
          <div className="stat-chip stat-inprocess"><span className="stat-num">{stats.inProcess}</span> In Process</div>
          <div className="stat-chip stat-deferred"><span className="stat-num">{stats.deferred}</span> Deferred</div>
          <div className="stat-chip stat-complete"><span className="stat-num">{stats.complete}</span> Complete</div>
          {stats.overdue > 0 && (
            <div className="stat-chip stat-overdue"><span className="stat-num">{stats.overdue}</span> Overdue</div>
          )}
        </div>

        <div className="controls">
          <div className="filters">
            <label className="filter-label">Filter by Status:</label>
            <select className="select" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>

            <label className="filter-label">Priority:</label>
            <select className="select" value={filterPriority} onChange={e => setFilterPriority(e.target.value)}>
              <option value="">All Priorities</option>
              {[1,2,3,4,5,6,7,8,9,10].map(p => <option key={p} value={p}>P{p}</option>)}
            </select>
          </div>

          <div className="sorting">
            <label className="filter-label">Sort by:</label>
            <select className="select" value={sortBy} onChange={e => setSortBy(e.target.value)}>
              <option value="created_at">Date Created</option>
              <option value="updated_at">Date Updated</option>
              <option value="due_date">Due Date</option>
              <option value="priority">Priority</option>
              <option value="title">Title</option>
              <option value="status">Status</option>
            </select>
            <button
              className="btn btn-sort"
              onClick={() => setSortOrder(o => o === 'asc' ? 'desc' : 'asc')}
              title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
            >
              {sortOrder === 'asc' ? '↑ Asc' : '↓ Desc'}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading"><div className="spinner"></div> Loading todos…</div>
        ) : todos.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h2>No todos found</h2>
            <p>Click <strong>New Todo</strong> to get started, or adjust your filters.</p>
          </div>
        ) : (
          <div className="todo-list">
            {todos.map(todo => (
              <div
                key={todo.id}
                className={`todo-card ${todo.is_overdue ? 'todo-overdue' : ''} ${todo.status === 'Complete' ? 'todo-complete' : ''}`}
              >
                <div className="todo-card-left">
                  <span
                    className="priority-badge"
                    style={{ backgroundColor: PRIORITY_COLORS(todo.priority) }}
                    title={`Priority ${todo.priority}`}
                  >
                    P{todo.priority}
                  </span>
                </div>

                <div className="todo-card-body">
                  <div className="todo-card-header">
                    <h3 className="todo-title">
                      {todo.title}
                      {todo.is_overdue && <span className="overdue-badge">⚠ Overdue</span>}
                    </h3>
                    <select
                      className="status-select"
                      value={todo.status}
                      style={{ borderColor: STATUS_COLORS[todo.status], color: STATUS_COLORS[todo.status] }}
                      onChange={e => handleStatusChange(todo, e.target.value)}
                    >
                      {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>

                  {todo.description && (
                    <p className="todo-description">{todo.description}</p>
                  )}

                  <div className="todo-meta">
                    <span className="meta-item">
                      <span className="meta-icon">📅</span>
                      Due: {formatDate(todo.due_date)}
                    </span>
                    <span className="meta-item">
                      <span className="meta-icon">🕐</span>
                      Added: {new Date(todo.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="todo-card-actions">
                  <button
                    className="btn btn-icon-only btn-edit"
                    onClick={() => openEditModal(todo)}
                    title="Edit"
                  >
                    ✏️
                  </button>
                  {deleteConfirmId === todo.id ? (
                    <div className="delete-confirm">
                      <span>Delete?</span>
                      <button className="btn btn-danger-sm" onClick={() => handleDelete(todo.id)}>Yes</button>
                      <button className="btn btn-cancel-sm" onClick={() => setDeleteConfirmId(null)}>No</button>
                    </div>
                  ) : (
                    <button
                      className="btn btn-icon-only btn-delete"
                      onClick={() => setDeleteConfirmId(todo.id)}
                      title="Delete"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {showModal && (
        <div className="modal-overlay" onClick={e => { if (e.target === e.currentTarget) closeModal(); }}>
          <div className="modal">
            <div className="modal-header">
              <h2>{editingTodo ? 'Edit Todo' : 'New Todo'}</h2>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            <form className="modal-form" onSubmit={handleSubmit}>
              {formErrors.submit && (
                <div className="alert alert-error">{formErrors.submit}</div>
              )}

              <div className="form-group">
                <label className="form-label">Title <span className="required">*</span></label>
                <input
                  className={`form-input ${formErrors.title ? 'input-error' : ''}`}
                  type="text"
                  name="title"
                  value={form.title}
                  onChange={handleFormChange}
                  placeholder="What needs to be done?"
                  maxLength={200}
                />
                {formErrors.title && <span className="field-error">{formErrors.title}</span>}
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  className="form-input form-textarea"
                  name="description"
                  value={form.description}
                  onChange={handleFormChange}
                  placeholder="Optional details…"
                  maxLength={1000}
                  rows={3}
                />
              </div>

              <div className="form-row">
                <div className="form-group form-group-half">
                  <label className="form-label">Due Date</label>
                  <input
                    className="form-input"
                    type="date"
                    name="due_date"
                    value={form.due_date}
                    onChange={handleFormChange}
                    min={today}
                  />
                </div>

                <div className="form-group form-group-half">
                  <label className="form-label">Priority (1=Highest) <span className="required">*</span></label>
                  <input
                    className={`form-input ${formErrors.priority ? 'input-error' : ''}`}
                    type="number"
                    name="priority"
                    value={form.priority}
                    onChange={handleFormChange}
                    min={1}
                    max={10}
                  />
                  {formErrors.priority && <span className="field-error">{formErrors.priority}</span>}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Status <span className="required">*</span></label>
                <select
                  className={`form-input ${formErrors.status ? 'input-error' : ''}`}
                  name="status"
                  value={form.status}
                  onChange={handleFormChange}
                >
                  {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                {formErrors.status && <span className="field-error">{formErrors.status}</span>}
              </div>

              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingTodo ? 'Save Changes' : 'Create Todo'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
