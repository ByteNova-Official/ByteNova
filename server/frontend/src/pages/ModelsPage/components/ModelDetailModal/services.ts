import http from '@/utils/http';

const { get, put } = http.create('ai');

export async function getModel({ id }) {
  return get(`/models/${id}`);
}
