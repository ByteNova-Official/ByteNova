import http from '@/utils/http';

const { post, put, del } = http.create('ai');

export async function createInferenceJob(params) {
  if (params.min_workers) params['min_workers'] = parseInt(params.min_workers);
  if (params.desired_workers) params['desired_workers'] = parseInt(params.desired_workers);
  if (params.max_workers) params['max_workers'] = parseInt(params.max_workers);
  return post('/inference_jobs', params);
}

export async function updateInferenceJobs(id, data) {
  let params = {}
  if (data.min_workers) params['min_workers'] = parseInt(data.min_workers);
  if (data.desired_workers) params['desired_workers'] = parseInt(data.desired_workers);
  if (data.max_workers) params['max_workers'] = parseInt(data.max_workers);
  if (data.job_assignment_type) params['job_assignment_type'] = data.job_assignment_type;
  if (data.scaling_type) params['scaling_type'] = data.scaling_type;

  return put('/inference_jobs/'+id, params);
}

export async function deleteInferenceJob(id) {
  return del('/inference_jobs/'+id);
}