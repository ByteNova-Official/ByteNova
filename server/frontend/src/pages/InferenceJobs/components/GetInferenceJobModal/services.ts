import http from '@/utils/http';

const { get, put } = http.create('ai');

export async function getInferenceJob({ id }) {
  return get(`/inference_jobs/${id}`);
}


export async function updateInferenceJobs(data) {
  const { id } = data;
  let params = {}
  if (data.min_workers) params['min_workers'] = data.min_workers.toInteger();
  if (data.desired_workers) params['desired_workers'] = data.desired_workers.toInteger();
  if (data.max_workers) params['max_workers'] = data.max_workers.toInteger();
  if (data.job_assignment_type) params['job_assignment_type'] = data.job_assignment_type;
  if (data.scaling_type) params['scaling_type'] = data.scaling_type;

  return put('/inference_jobs/'+id, params);
}
