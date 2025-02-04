// 全局共享数据示例
import { useRequest } from '@umijs/max';
import * as services from '../services/global';
import { useEffect } from 'react';

const useGlobal = () => {

  const getUsers = useRequest(services.getUsers, {
    manual: true,
  })
  const getModels = useRequest(services.getModels, {
    manual: true,
  });
  const getJobs = useRequest(services.getJobs, {
    manual: true,
  }); 
  const getInvocations = useRequest(services.getInvocations, {
    manual: true,
  });
  const getWorkers = useRequest(services.getWorks, {
    manual: true,
  });

  const getBaseInfo = () => {
    getUsers.run();
    getModels.run();
    getJobs.run();
    getInvocations.run();
    getWorkers.run();
  }

  useEffect(() => {
    if (localStorage.token) {
      getBaseInfo();
    }
  }, [])

  return {
    getUsers,
    getModels,
    getJobs,
    getInvocations,
    getWorkers,
    getBaseInfo,
  };
};

export default useGlobal;
