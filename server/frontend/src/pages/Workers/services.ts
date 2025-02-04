import http from '@/utils/http';

const { post, put, del } = http.create('ai');

export async function createWorker(params) {
  return post('/inference_jobs', params);
}

export async function updateWorker(id, data) {
  let params = {}
  if (data.working_on) params['working_on'] = data.working_on;
  if (data.job_assignment_type) params['job_assignment_type'] = data.job_assignment_type;
  if (data.type) params['type'] = data.type;

  return put('/workers/'+id, params);
}

export async function deleteWorker(id) {
  return del('/workers/'+id);
}
