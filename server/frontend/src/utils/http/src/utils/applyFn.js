export default (fn, params) => (typeof fn === 'function' ? fn(params) : fn);
