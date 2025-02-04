import { history } from '@umijs/max';
import Http from './src';

export default new Http({
  contentKey: '',
  // servers: process.config.servers,
  header({ domain }) {
    const headers = {};
    const token = localStorage['token'];

    if (token) {
      headers['X-API-Key'] = token;
    }

    return headers;
  },
  afterAuthorityFailure() {
    history.push('/user/login')
  },
});
