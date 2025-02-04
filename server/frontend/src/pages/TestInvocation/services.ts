import http from '@/utils/http';

const { post } = http.create('ai');

export async function postJob(params) {
  const { jobId, ...rest } = params || {};
  return post(`/inference_jobs/${jobId}/invoke_sync`, rest);
}