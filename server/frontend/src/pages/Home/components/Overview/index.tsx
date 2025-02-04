import { ProCard } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { Space, Typography } from 'antd';
import * as React from 'react';

const Overview = () => {
  const state = useModel('global');
  console.log('state', state)
  const { getUsers, getModels, getJobs, getInvocations, getWorkers }  = state || {};

  const user = getUsers.data;
  const models = getModels.data;
  const jobs = getJobs.data;
  const invocations = getInvocations.data;
  const workers = getWorkers.data;
  

  return (
    <Space direction="vertical" size={24} style={{ width: '100%' }}>
      <ProCard title="User Info" bordered loading={!user}>
        <div>Name: {user?.name}</div>
        <div>Email: {user?.email}</div>
        <div>Company: {user?.company}</div>
        <div>
          Verification: {user?.verified_at ? "Email verified" : "Email not verified yet"}
        </div>
      </ProCard>
      <ProCard title="AI Usages" bordered>
        <div>Models: {(models || []).length}</div>
        <div>Inference Jobs: {(jobs || []).length}</div>
        <div>Invocations: {invocations?.length}</div>
      </ProCard>
      <ProCard title="Compute Contribute" bordered>
        <div>Workers: {workers?.length}</div>
      </ProCard>
      <ProCard title="API Key" bordered>
      <div>{localStorage.token}</div>
      </ProCard>
    </Space>
  );
}
 
export default Overview;