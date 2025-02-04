import { PageContainer, ProTable, EditableProTable } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { PlusOutlined } from '@ant-design/icons';
import { Button, Space, Modal } from 'antd';
import { useEffect, useState } from 'react';
import { useColumnsState }  from '@/hooks';
import CreateModelModal from './components/CreateModelModal';
import ModelDetailModal from './components/ModelDetailModal';

import {createModel, updateModel, deleteModel} from './services';

import './index.less';

const ModelPage: React.FC = () => {
  const [columnsStateMap, setColumnsStateMap] = useColumnsState({
    artifact: {
      show: false,
    },
    version: {
      show: false,
    },
    invoke_function: {
      show: false,
    },
    runtime_docker_image: {
      show: false,
    },
    example_input: {
      show: false,
    },
    created_at: {
      show: false,
    },
    updated_at: {
      show: false,
    },
  }, "columns_model_config");

  const { getModels, getUsers } = useModel('global');
  const [visible, setVisible] = useState(false);
  const [detailId, setDetailId] = useState();
  const [detailModalVisible, setDetailModalVisible] = useState(false); // 详情modal
  const [dataSource, setDataSource] = useState<readonly any[]>([]);
  const [editableKeys, setEditableRowKeys] = useState<React.Key[]>([]);

  const { id: userId } = getUsers.data || {};

  const { run, loading } = useRequest(createModel, {
    manual: true,
  })
  
  const data = getModels.data;

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
      editable: false,
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
      title: 'Model ID',
      editable: false,
      sorter: (a, b) => (a['id'] || '').localeCompare(b['id'] || ''),
      sortDirections: ['id'], 
      ellipsis: true,
    },
    {
      dataIndex: 'model_type',
      title: 'Type',
      editable: false,
      sorter: (a, b) => (a['model_type'] || '').localeCompare(b['model_type'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'required_gpu',
      title: 'Required GPU',
      editable: true,
      sorter: (a, b) => (a['required_gpu'] || 0) - (b['required_gpu'] || 0),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'visibility',
      title: 'Visibility',
      editable: true,
      render(val) {
        const style = val == 'public' ? { color: 'blue' } : { color: 'black' };
        return <span style={style}>{val == 'public' ? 'Public' : 'Private'}</span>;
      },
      sorter: (a, b) => (a['visibility'] || '').localeCompare(b['visibility'] || ''),
      sortDirections: ['ascend', 'descend'], 
    },
    {
      dataIndex: 'artifact',
      title: 'Artifact Repo',
      editable: false,
      sorter: (a, b) => (a['artifact'] || '').localeCompare(b['artifact'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'version',
      title: 'Version SHA',
      editable: true,
      sorter: (a, b) => (a['version'] || '').localeCompare(b['version'] || ''),
      sortDirections: ['version'], 
      ellipsis: true,
    },
    {
      dataIndex: 'invoke_function',
      title: 'Invoke Function',
      editable: true,
      sorter: (a, b) => (a['invoke_function'] || '').localeCompare(b['invoke_function'] || ''),
      sortDirections: ['ascend', 'descend'], 
      ellipsis: true,
    },
    {
      dataIndex: 'runtime_docker_image',
      title: 'Runtime Docker Image',
      editable: true,
      sorter: (a, b) => (a['runtime_docker_image'] || '').localeCompare(b['runtime_docker_image'] || ''),
      sortDirections: ['runtime_docker_image'], 
      ellipsis: true,
    },
    {
      dataIndex: 'description',
      title: 'Description',
      editable: true,
      sorter: (a, b) => (a['description'] || '').localeCompare(b['description'] || ''),
      sortDirections: ['description'], 
      ellipsis: true,
    },
    {
      dataIndex: 'example_input',
      title: 'Example Input',
      editable: true,
      sorter: (a, b) => (a['example_input'] || '').localeCompare(b['example_input'] || ''),
      sortDirections: ['example_input'], 
      ellipsis: true,
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
                 await deleteModel(record.id);
                 await getModels.run();
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
    loading: getModels.loading,
    tableLayout: "auto",
    cardBordered: true,
    recordCreatorProps: false,
    editable: {
      type: 'multiple',
      editableKeys,
      onSave: async (rowKey, row) => {
        console.log(rowKey, row);
        await updateModel(rowKey, row);
        await getModels.run();
      },
      onChange: setEditableRowKeys,
      actionRender: (row, config, dom) => [dom.save, dom.cancel],
    },
    search: false,
    options: {
      setting: {
        listsHeight: 400,
      },
      reload: () => getModels.run(),
    },
    value: dataSource,
    onChange: setDataSource,
    dateFormatter: "string",
    columnsState: {
      value: columnsStateMap,
      onChange: setColumnsStateMap,
    },
    pagination: false,
  }

  return (
    <PageContainer ghost>
      <Space direction="vertical" size={32} style={{ width: '100%' }}>
        <EditableProTable
          {...defaultOptions}
          headerTitle="My Models"
          toolBarRender={() => [
            <Button
              key="button"
              icon={<PlusOutlined />}
              loading={loading}
              type="primary"
              onClick={() => setVisible(true)}
            >
              Create new model
            </Button>
          ]}
          value={(dataSource || []).filter(item => item['user_id'] === userId)}
        />
        <EditableProTable
          {...defaultOptions}
          columns={columns.filter(item => item.dataIndex !== 'action')}
          headerTitle="Public Models"
          value={(dataSource || []).filter(item => item.visibility === 'public')}
        />
      </Space>
      <CreateModelModal visible={visible} onClose={() => setVisible(false)} />
      <ModelDetailModal
        id={detailId}
        visible={detailModalVisible}
        onClose={() => setDetailModalVisible(false)}
      />
    </PageContainer>
  );
};

export default ModelPage;
