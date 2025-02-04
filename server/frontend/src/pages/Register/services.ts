import http from '@/utils/http';

const { post } = http.create('ai');

export async function doSignup(params: any) {
  return post('/users', params);
}

export async function doLogin(params: any) {
  return post('/login', params);
}
