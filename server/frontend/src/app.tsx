// 运行时配置
import { history, useModel, useRequest } from "@umijs/max";
import iconLogo from './assets/logo.png';
import * as services from './services/global';
import { useEffect } from "react";
import UserAction from './components/UserAction';
import { message } from 'antd';

message.config({
  duration: 3,
  maxCount: 1,
});


// 全局初始化数据配置，用于 Layout 用户信息和权限初始化
// 更多信息见文档：https://umijs.org/docs/apiruntime-config#getinitialstate
export async function getInitialState(): Promise<{
  name?: string,
  user?: object,
  models?: any[],
  jobs?: any[],
  invocations?: any[],
  workers?: any[],
  fetchGlobalData?: () => void,
}> {


  if (window.location.pathname.indexOf('/user/') === -1) {
    if (!localStorage.token) {
      history.push('/user/login')
      return {};
    }
  }

  return {};
}

export const layout = ({ initialState }) => {
  return {
    logo: iconLogo,
    menu: {
      locale: false,
    },
    rightRender: () => <UserAction initialState={initialState} />,
  };
};
