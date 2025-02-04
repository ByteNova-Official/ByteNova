import http from '@/utils/http';

const { post, put, del } = http.create('ai');

export async function createModel(params) {
  if (params.required_gpu) params['required_gpu'] = parseInt(params.required_gpu);
  return post('/models', params);
}

export async function createDeafultInferenceJob(params) {
  if(!('set_as_model_default' in params)){
    params["set_as_model_default"]=true;
  }
  return post('/inference_jobs', params);
}

export async function updateModel(id, data) {
  let params = {}
  if (data.visibility) params['visibility'] = data.visibility;
  if (data.required_gpu) params['required_gpu'] = data.required_gpu - 0;
  if (data.version) params['version'] = data.version;
  if (data.invoke_function) params['invoke_function'] = data.invoke_function;
  if (data.runtime_docker_image) params['runtime_docker_image'] = data.runtime_docker_image;
  if (data.description) params['description'] = data.description;
  if (data.example_input) params['example_input'] = data.example_input;

  return put('/models/'+id, params);
}

export async function deleteModel(id) {
  return del('/models/'+id);
}