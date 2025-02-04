import { PageContainer, ProTable } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Space } from 'antd';
import { useState, useEffect } from 'react';
import InvocationDetailModal from './components/InvocationDetailModal';
import './index.less';

const Invocations: React.FC = () => {
  const { getInvocations } = useModel('global');
  const [detailId, setDetailId] = useState();
  const [detailModalVisible, setDetailModalVisible] = useState(false); // 详情modal

  const models = getInvocations.data;

  useEffect(() => {
    getInvocations.run();
  }, [])

  const handleDetailModalVisible = (id) => {
    setDetailId(id);
    setDetailModalVisible(true);
  }

  const columns = [
    {
      dataIndex: 'id',
      title: 'ID',
      render(id) {
        return (
          <a className="title" onClick={() => handleDetailModalVisible(id)}>
            {id}
          </a>
        )
      }
    },
    {
      dataIndex: 'status',
      title: 'Status',
      ellipsis: true,
      sorter: (a, b) => (a['status'] || '').localeCompare(b['status'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'inference_job_name',
      title: 'Job',
      ellipsis: true,
      sorter: (a, b) => (a['inference_job_name'] || '').localeCompare(b['inference_job_name'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'processed_by_worker_name',
      title: 'Worker Name',
      ellipsis: true,
    },
    {
      dataIndex: 'input',
      title: 'Input',
      ellipsis: true,
    },
    {
      dataIndex: 'error',
      title: 'Error',
      ellipsis: true,
    },
    {
      dataIndex: 'result',
      title: 'Result',
      ellipsis: true,
    },
    {
      dataIndex: 'created_at',
      title: 'Created time',
      sorter: (a, b) => {
        const dateA = new Date(a['created_at']);
        const dateB = new Date(b['created_at']);
        return dateA - dateB;
      },
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'process_start_time',
      title: 'Process Start Time',
      sorter: (a, b) => {
        const dateA = new Date(a['process_start_time']);
        const dateB = new Date(b['process_start_time']);
        return dateA - dateB;
      },
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      dataIndex: 'process_finish_time',
      title: 'Process Finish Time',
      sorter: (a, b) => {
        const dateA = new Date(a['process_finish_time']);
        const dateB = new Date(b['process_finish_time']);
        return dateA - dateB;
      },
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
  ]

  return (
    <PageContainer ghost>
      <Space direction="vertical" size={32} style={{ width: '100%' }}>
        <ProTable
          columns={columns}
          dataSource={models}
          loading={getInvocations.loading}
          cardBordered
          editable={{
            type: 'multiple',
          }}
          search={false}
          columnsState={{
            persistenceKey: 'pro-table-singe-demos',
            persistenceType: 'localStorage',
            onChange(value) {
              // console.log('value: ', value);
            },
          }}
          rowKey="id"
          options={{
            reload: () => getInvocations.run(),
            setting: {
              listsHeight: 400,
            },
          }}
          pagination={true}
          dateFormatter="string"
          headerTitle="Invocations"
        />
      </Space>
      <InvocationDetailModal
        id={detailId}
        visible={detailModalVisible}
        onClose={() => setDetailModalVisible(false)}
      />
    </PageContainer>
  );
};

export default Invocations;
