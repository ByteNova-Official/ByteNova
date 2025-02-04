import { message } from 'antd';
import { history } from '@umijs/max';
import applyFn from './utils/applyFn';

/*
 * request query 中间件
 */
export const query = {
  success(config) {
    // if (baseURL.includes('play')) {
    //   // 接口的参数不放在url上面的请求列表
    //   const noQueryList = [
    //     'evaluate-comment', // 订单评论
    //     'getConnectPaypalUrl', // 获取paypal绑卡回调地址
    //   ];
    //   const isAddParams = noQueryList.every((item) => !url.includes(item));

    //   if (isAddParams) config.params = data;
    // }

    return config;
  },
};

/*
 * request header 中间件
 */
export const header = {
  success(config) {
    const { header } = config;

    if (header) {
      const headers = applyFn(header, config);
      config.headers = { ...headers, ...config.headers };
    }

    return config;
  },
};

/*
 * request 加密 中间件
 */
export const addKey = {
  success(config) {
    const { headers, data, domain, url } = config;
    const { encrypt, _tk_ } = headers;


    return config;
  },
};

/*
 * response data 状态处理中间件
 */
const defaultErrorValidate = (data) => {
  return data.status && data.status.toUpperCase() === 'ERROR';
};

export const dataStatus = {
  success(response) {
    const { data, config } = response;
    const { responseDataValidator } = config;

    if ((responseDataValidator || defaultErrorValidate)(data)) {
      return Promise.reject(response);
    }

    return response;
  },
};

/*
 * 授权处理中间件，检查是否非法授权
 */
const defaultOptions = {
  codes: ['50008', '50012', '50014', '50016', '10050005', '10050006']
};

let hasErrorMessage = false;
const DEFAULT_EXPIRE_MESSAGE = 'Please log in';

export const authorityValidator = {
  error(response) {
    const { data = {}, config } = response;

    /* eslint-disable no-shadow */
    const { authorityValidator, authorityFailureCodes, afterAuthorityFailure } = config || {};
    const authorityOptions = defaultOptions;

    if (authorityValidator) {
      return Promise.reject(authorityValidator(data) || data);
    }

    if (authorityFailureCodes) {
      authorityOptions.codes = authorityFailureCodes;
    }

    const { error } = data;
    if (error) {
      if (!hasErrorMessage) {
        // const errorMessage = data.errorMsg || DEFAULT_EXPIRE_MESSAGE;
        // message.warning(errorMessage, 2, () => (hasErrorMessage = false));

        if (afterAuthorityFailure) {
          afterAuthorityFailure(data, config);
        }

        hasErrorMessage = true;
      }

      config.ignoreErrorModal = true;
    }

    return Promise.reject(response);
  },
};

/*
 * responseError 错误处理
 */
const DEFAULT_RES_ERROR = 'System exception, please try again later';
let hasErrorModal = false;

const responseError = {
  error(response) {
    if (response.config && !response.config.ignoreErrorModal && !hasErrorModal) {
      message.error(
        response?.response.data?.error || DEFAULT_RES_ERROR,
        2,
        () => (hasErrorMessage = false),
      );
    }
    if (response?.response && response?.response?.data.error === 'Invalid API key') {
      history.push('/user/login')
    }
    return Promise.reject(response);
  },
};

/*
 * response data 内容处理中间件
 */
export const dataContent = {
  success(response) {
    const key = response.config.contentKey;

    // if (key) {
    //   return response.data[key];
    // }

    return response;
  },
};

export default {
  request: [query, header, addKey].reverse(),
  response: [dataStatus, authorityValidator, responseError, dataContent],
};
