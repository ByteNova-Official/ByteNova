import { PageContainer, EditableProTable } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { Button, Space, Modal } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import CreateInferenceJobModal from './components/CreateInferenceJobModal';
import GetInferenceJobModal from './components/GetInferenceJobModal';
import { useState, useEffect } from 'react';
import { useColumnsState }  from '@/hooks';

import { updateInferenceJobs, deleteInferenceJob } from './services';

import './index.less';


const InferenceJobs: React.FC = () => {
  const [columnsStateMap, setColumnsStateMap] = useColumnsState(
    {
      name: {
        show: true,
      },
      id: {
        show: true,
      },
      model_name: {
        show: true,
      },
      model_id: {
        show: false,
      },
      visibility: {
        show: true,
      },
      active_workers: {
        show: true,
      },
      min_workers: {
        show: false,
      },
      desired_workers: {
        show: false,
      },
      max_workers: {
        show: false,
      },
      job_assignment_type: {
        show: false,
      },
      scaling_type: {
        show: true,
      },
      model_required_gpu: {
        show: true,
      },
      model_artifact: {
        show: false,
      },
      model_version: {
        show: false,
      },
      description: {
        show: true,
      },
      model_example_input: {
        show: false,
      },
      created_at: {
        show: false,
      },
      updated_at: {
        show: false,
      },
      _id: {
        show: true,
      },
    },
    "columns_inference_config"
  );

  const { getJobs, getInvocations, getModels, getUsers } = useModel('global');
  const [visible, setVisible] = useState(false); // 创建modal
  const [detailId, setDetailId] = useState();
  const [detailModalVisible, setDetailModalVisible] = useState(false); // 详情modal
  const [editableKeys, setEditableRowKeys] = useState<React.Key[]>([]);
  const [dataSource, setDataSource] = useState<readonly any[]>([]);
  
  const { id: userId } = getUsers.data || {};

  const { run, loading } = useRequest(CreateInferenceJobModal, {
    manual: true,
  })

  const data = getJobs.data;
  const invocations = getInvocations.data || [];

  useEffect(() => {
    getJobs.run();
    getModels.run();
    getInvocations.run();
  }, [])

  useEffect(() => {
    setDataSource(data);
  }, [data])

  const handleDetailModalVisible = (id) => {
    setDetailId(id);
    setDetailModalVisible(true);
  }

  const columns = [
    {
      dataIndex: 'name',
      title: 'Name',
      sorter: (a, b) => (a['name'] || '').localeCompare(b['name'] || ''),
      sortDirections: ['ascend', 'descend'], 
      render(value, { id }) {
        return (
          <a className="title" onClick={() => handleDetailModalVisible(id)}>
            {value}
          </a>
        )
      }
    },
    {
      dataIndex: 'id',
      title: 'ID',
      editable: false,
      sorter: (a, b) => (a['id'] || '').localeCompare(b['id'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'model_name',
      title: 'Model',
      editable: false,
      sorter: (a, b) => (a['model_name'] || '').localeCompare(b['model_name'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      dataIndex: 'model_id',
      title: 'Model ID',
      editable: false,
      sorter: (a, b) => (a['model_id'] || '').localeCompare(b['model_id'] || ''),
      sortDirections: ['ascend', 'descend'],
      ellipsis: true,
    },
    {
      dataIndex: 'visibility',
      title: 'Visibility',
      editable: false,
      render(val) {
        const style = val == 'public' ? { color: 'blue' } : { color: 'black' };
        return <span style={style}>{val == 'public' ? 'Public' : 'Private'}</span>;
      },
      sorter: (a, b) => (a['visibility'] || '').localeCompare(b['visibility'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'active_workers',
      title: 'Active workers',
      editable: false,
      sorter: (a, b) => (a['active_workers'] || 0) - (b['active_workers'] || 0),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'min_workers',
      title: 'Minimum Workers',
      editable: true,
      sorter: (a, b) => (a['min_workers'] || 0) - (b['min_workers'] || 0),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'desired_workers',
      title: 'Desired Workers',
      editable: true,
      sorter: (a, b) => (a['desired_workers'] || 0) - (b['desired_workers'] || 0),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'max_workers',
      title: 'Maximum Workers',
      editable: true,
      sorter: (a, b) => (a['max_workers'] || 0) - (b['max_workers'] || 0),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'job_assignment_type',
      title: 'Job Assignment Type',
      editable: true,
      sorter: (a, b) => (a['job_assignment_type'] || '').localeCompare(b['job_assignment_type'] || ''),
      ellipsis: true,
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'scaling_type',
      title: 'Scaling',
      editable: true,
      sorter: (a, b) => (a['scaling_type'] || '').localeCompare(b['scaling_type'] || ''),
      ellipsis: true,
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'model_required_gpu',
      title: 'GPU Required',
      editable: false,
      sorter: (a, b) => (a['model_required_gpu'] || 0) - (b['model_required_gpu'] || 0),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'model_artifact',
      title: 'Model Repo',
      editable: false,
      sorter: (a, b) => (a['model_artifact'] || 0) - (b['model_artifact'] || 0),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'model_version',
      title: 'Model Version',
      editable: false,
      sorter: (a, b) => (a['model_version'] || 0) - (b['model_version'] || 0),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'description',
      title: 'Description',
      editable: false,
      sorter: (a, b) => (a['description'] || '').localeCompare(b['description'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'model_example_input',
      title: 'Example Input',
      editable: false,
      sorter: (a, b) => (a['model_example_input'] || '').localeCompare(b['model_example_input'] || ''),
      ellipsis: true,
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'created_at',
      title: 'Created at',
      editable: false,
      sorter: (a, b) => {
        const dateA = new Date(a['created_at']);
        const dateB = new Date(b['created_at']);
        return dateA - dateB;
      },
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },

    {
      dataIndex: 'updated_at',
      title: 'Updated at',
      editable: false,
      sorter: (a, b) => {
        const dateA = new Date(a['updated_at']);
        const dateB = new Date(b['updated_at']);
        return dateA - dateB;
      },
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: '_id',
      title: 'Total Invocations',
      editable: false,
      render(_, { id }) {
        return (invocations || []).filter(invocation => invocation.inference_job_id === id).length
      },
      ellipsis: true,
    },
    {
      dataIndex: 'action',
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
                await deleteInferenceJob(record.id);
                await getJobs.run();
              },
            })
          }}
        >
          Delete
        </a>
      ],
    }
  ]

  const defaultOptions = {
    rowKey: 'id',
    columns,
    loading: getJobs.loading,
    tableLayout: "auto",
    cardBordered: true,
    recordCreatorProps: false,
    editable: {
      type: 'multiple',
      editableKeys,
      onSave: async (rowKey, row) => {
        await updateInferenceJobs(rowKey, row);
        await getJobs.run();
      },
      onChange: setEditableRowKeys,
      actionRender: (row, config, dom) => [dom.save, dom.cancel],
    },
    search: false,
    options: {
      setting: {
        listsHeight: 400,
      },
      reload: () => getJobs.run(),
    },
    value: dataSource,
    onChange: setDataSource,
    columnsState: {
      value: columnsStateMap,
      onChange: setColumnsStateMap,
    },
    pagination: false,
    dateFormatter: "string",
  }

  return (
    <div>
      <PageContainer ghost>
        <Space direction="vertical" size={32} style={{ width: '100%' }}>
          <EditableProTable
            {...defaultOptions}
            headerTitle="My Jobs"
            toolBarRender={() => [
              <Button
                  key="button"
                  icon={<PlusOutlined />}
                  loading={loading}
                  type="primary"
                  onClick={() => setVisible(true)}
                >
                  Create new Job
                </Button>
              ,
            ]}
            value={(dataSource || []).filter(item => item['user_id'] === userId)}
          />
          <EditableProTable
            {...defaultOptions}
            headerTitle="Public Jobs"
            columns={columns.filter(item => item.dataIndex !== 'action')}
            value={(dataSource || []).filter(item => item.visibility === 'public')}
          />
        </Space>
        <CreateInferenceJobModal visible={visible} onClose={() => setVisible(false)} />
        <GetInferenceJobModal
          id={detailId}
          visible={detailModalVisible}
          onClose={() => setDetailModalVisible(false)}
        />
      </PageContainer>
    </div>
  );
};

export default InferenceJobs;
