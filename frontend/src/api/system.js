import request from './request'

// 用户管理API
export const userAPI = {
  getUsers: (params) => request.get('/api/admin/users', { params }),
  createUser: (data) => request.post('/api/admin/users', data),
  updateUser: (id, data) => request.put(`/api/admin/users/${id}`, data),
  deleteUser: (id) => request.delete(`/api/admin/users/${id}`),
  assignRole: (userId, roleId) => request.post(`/api/admin/users/${userId}/roles`, { roleId }),
  removeRole: (userId, roleId) => request.delete(`/api/admin/users/${userId}/roles/${roleId}`)
}

// 角色管理API
export const roleAPI = {
  getRoles: (params) => request.get('/api/admin/roles', { params }),
  createRole: (data) => request.post('/api/admin/roles', data),
  updateRole: (id, data) => request.put(`/api/admin/roles/${id}`, data),
  deleteRole: (id) => request.delete(`/api/admin/roles/${id}`),
  assignPermission: (roleId, permissions) => request.post(`/api/admin/roles/${roleId}/permissions`, { permissions })
}

// 任务管理API扩展
export const taskAPI = {
  getJobExecutions: (jobId, params) => request.get(`/api/task/scheduler/jobs/${jobId}/executions`, { params }),
  runJobWithParams: (jobId, params) => request.post(`/api/task/scheduler/jobs/${jobId}/run`, params),
  pauseJob: (jobId) => request.post(`/api/task/scheduler/jobs/${jobId}/pause`),
  resumeJob: (jobId) => request.post(`/api/task/scheduler/jobs/${jobId}/resume`)
}