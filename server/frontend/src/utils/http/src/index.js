import Request from './Request';
import interceptors from './interceptors';

export default class Http extends Request {
  options;

  interceptors;

  constructor(options) {
    super();

    this.options = {
      contentType: 'json',
      ...options,
    };
    this.interceptors = interceptors;
  }
  static create(options) {
    return new Http(options);
  }

  create(domain) {
    return {
      get: (...args) => this.axiosRequest('get', domain, ...args),
      post: (...args) => this.axiosRequest('post', domain, ...args),
      del: (...args) => this.axiosRequest('delete', domain, ...args),
      put: (...args) => this.axiosRequest('put', domain, ...args),
      patch: (...args) => this.axiosRequest('patch', domain, ...args),
      head: (...args) => this.axiosRequest('head', domain, ...args),
    };
  }
}
