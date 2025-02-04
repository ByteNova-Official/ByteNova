import axios from 'axios';

export default class Request {
  options;

  interceptors;

  axiosRequest(...args) {
    const [method, domain, url, data, options] = args;

    const services = {
      ai: process.env.REACT_APP_BACKEND_SERVER_URL
    };

    let config = {
      domain,
      baseURL: services[domain] || services.qa,
      url,
      method,
    };

    if (['get'].includes(method)) {
      config.params = data;
    } else {
      config.data = data;
    }

    config = {
      ...config,
      ...this.options,
      ...options,
    };

    const instance = axios.create();

    for (let interceptor of this.interceptors.request) {
      instance.interceptors.request.use(interceptor.success);
    }

    for (let interceptor of this.interceptors.response) {
      // interceptor = applyFn(interceptor, { axiosRequest: this.axiosRequest.bind(this, ...args) });

      const { success = null, error = null } = interceptor;

      instance.interceptors.response.use(success, error);
    }

    return instance.request(config);
  }
}
