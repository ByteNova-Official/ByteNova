import http from '@/utils/http';

const { get, put } = http.create('ai');

export async function getInvocation({ id }) {
  return get(`/invocations/${id}`);
}
