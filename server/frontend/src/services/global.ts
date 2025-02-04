import http from '@/utils/http';

const { get: post } = http.create('ai');

export async function getUsers() {
  return post('/users');
}

export async function getModels() {
  return post('/models');
}

export async function getJobs() {
  return post('/inference_jobs');
}

export async function getInvocations() {
  return post('/invocations');
}

export async function getWorks() {
  return post('/workers');
}

