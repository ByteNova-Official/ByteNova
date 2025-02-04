import { PageContainer, ProTable, EditableProTable } from '@ant-design/pro-components';
import { useModel } from '@umijs/max';
import { Space, Modal } from 'antd';
import { useEffect, useState } from 'react';
import { updateWorker, deleteWorker } from './services';

const Workers: React.FC = () => {
  const { getJobs, getWorkers } = useModel('global');

  const data = getWorkers.data;
  const jobs = getJobs.data || [];
  const [dataSource, setDataSource] = useState<readonly any[]>([]);
  const [editableKeys, setEditableRowKeys] = useState<React.Key[]>([]);

  useEffect(() => {
    getWorkers.run();
  }, [])

  useEffect(() => {
    setDataSource(data);
  }, [data])

  console.log('workers', data);

  const columns = [
    {
      dataIndex: 'id',
      title: 'ID',
      sorter: (a, b) => (a['id'] || '').localeCompare(b['id'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
      editable: false,
    },
    {
      dataIndex: 'name',
      title: 'Name',
      sorter: (a, b) => (a['name'] || '').localeCompare(b['name'] || ''),
      sortDirections: ['ascend', 'descend'], 
      editable: false,
    },
    {
      dataIndex: 'status',
      title: 'Status',
      sorter: (a, b) => (a['status'] || '').localeCompare(b['status'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
      editable: false,
    },
    {
      dataIndex: 'connected',
      title: 'Connected',
      render(val) {
        const style = val ? { color: 'green' } : { color: 'grey' };
        return <span style={style}>{val ? 'Yes' : 'No'}</span>;
      },
      sorter: (a, b) => b['connected'] - a['connected'],
      sortDirections: ['ascend', 'descend'], 
      editable: false,
    },
    {
      dataIndex: 'working_on',
      title: 'Working on job',
      render(val) {
        return (jobs || []).filter(job => job.id === val)[0]?.name;
      },
      sorter: (a, b) => (a['working_on'] || '').localeCompare(b['working_on'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'info',
      title: 'Host info',
      sorter: (a, b) => (a['info'] || '').localeCompare(b['info'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
      editable: false,
    },
    {
      dataIndex: 'available_gpu',
      title: 'Available GPU',
      sorter: (a, b) => (a['available_gpu'] || '').localeCompare(b['available_gpu'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      dataIndex: 'type',
      title: 'Type',
      sorter: (a, b) => (a['type'] || '').localeCompare(b['type'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      dataIndex: 'job_assignment_type',
      title: 'Job Assignment',
      sorter: (a, b) => (a['job_assignment_type'] || '').localeCompare(b['job_assignment_type'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      title: 'Action',
      valueType: 'option',
      render: (text, record, _, action) => [
        <a
          key="editable"
          onClick={() => {
            action?.startEditable?.(record.id);
          }}
        >
          Edit
        </a>,
        <a
          key="delete"
          onClick={() => {
            Modal.confirm({
              title: 'Tips',
              content: 'Are you sure you want to delete?',
              onOk: async () => {
                await deleteWorker(record.id);
                await getWorkers.run();
              },
            });
          }}
        >
          Delete
        </a>
      ],
    }
  ]

  return (
    <PageContainer ghost>
      <link rel="icon" href="https://cdn.clustro.ai/icon.ico" type="image/x-icon"></link>
      <Space direction="vertical" size={32} style={{ width: '100%' }}>
        <EditableProTable
          columns={columns}
          rowKey="id"
          loading={getWorkers.loading}
          tableLayout="auto"
          cardBordered
          recordCreatorProps={false}
          editable={{
            type: 'multiple',
            editableKeys,
            onSave: async (rowKey, row) => {
              console.log(rowKey, row);
              updateWorker(rowKey, row);
            },
            onChange: setEditableRowKeys,
            actionRender: (row, config, dom) => [dom.save, dom.cancel],
          }}
          options={{
            reload: () => getWorkers.run(),
            setting: {
              listsHeight: 400,
            },
          }}
          value={dataSource}
          onChange={setDataSource}
          dateFormatter="string"
          pagination={false}
          dateFormatter="string"
          headerTitle="Workers"
        />
      </Space>
    </PageContainer>
  );
};

export default Workers;
