import * as React from 'react';
import { useState, useEffect, useRef } from 'react';
import { Modal, Descriptions, Skeleton, Switch, Form, Input } from 'antd';
import { ProField, ProForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';


import { useRequest, useModel } from '@umijs/max';
import { getInferenceJob, updateInferenceJobs } from './services';

import styles from './index.less';

enum Mode {
  READ = 'read',
  EDIT = 'edit',
}

const GetInferenceJobModal = ({
  id,
  visible,
  onClose,
}) => {
  const [mode, setMode] = useState(Mode.READ);
  const { getInvocations, getUsers } = useModel('global');
  const formRef = useRef();

  
  const { id: userId } = getUsers.data || {};

  const invocations = getInvocations.data || [];

  const { run, loading, data } = useRequest(() => getInferenceJob({ id }), {
    manual: true,
  });

  const updateJobReq = useRequest(params => updateInferenceJobs({ id, ...params }), {
    manual: true,
  });

  useEffect(() => {
    if (visible && id) {
      setMode(Mode.READ)
      run();
    }
  }, [visible, id])

  const { name, model_name, updated_at, visibility, active_workers, desired_workers, max_workers, min_workers, description, enabled, model_required_gpu, scaling_type, model_example_input, user_id } = data || {};
  const totalInvocations = (invocations || []).filter(invocation => invocation.inference_job_id === id).length;

  const isOwnerItem = user_id && userId && user_id === userId;

  const handleSwitch = (checked) => {
    if (!checked) {
      formRef.current?.resetFields();
    }
    setMode(checked ? Mode.EDIT : Mode.READ)
  }

  const handleConfirm = async () => {
    if (mode !== Mode.READ) {
      const resp = await formRef.current?.validateFieldsReturnFormatValue?.()
      await updateJobReq.run(resp);
    }
    onListUpdate();
    onClose()
  }

  return (
    <Modal
      title="Inference Job"
      width={640}
      open={visible}
      onCancel={onClose}
      confirmLoading={updateJobReq.loading}
      destroyOnClose
      onOk={onClose}
    >
      <div className={styles.modal}>
        <Skeleton loading={loading} active>
          <ProForm
            readonly
            submitter={{ render: () => [] }}
            onFinish={async (value) => console.log(value)}
          >
            <Descriptions column={1}>
              <Descriptions.Item label="ID">
                <ProField text={id} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Name">
                <ProField text={name} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Last Modify">
                <ProField text={updated_at} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Model">
                <ProField text={model_name} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Visibility">
                <ProField text={visibility} />
              </Descriptions.Item>

              <Descriptions.Item label="Active workers">
                <ProField text={active_workers} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Minimum Workers">
                <ProField text={min_workers} />
              </Descriptions.Item>

              <Descriptions.Item label="Desired Workers">
                <ProField text={desired_workers} />
              </Descriptions.Item>

              <Descriptions.Item label="Maximum Workers">
                <ProField text={max_workers} />
              </Descriptions.Item>

              <Descriptions.Item label="Scaling">
                <ProField text={scaling_type} />
              </Descriptions.Item>

              <Descriptions.Item label="GPU Required">
                <ProField text={model_required_gpu} />
              </Descriptions.Item>

              <Descriptions.Item label="Total Invocations">
                <ProField text={totalInvocations} mode="read" />
              </Descriptions.Item>

              <Descriptions.Item label="Description">
                <ProField text={description} />
              </Descriptions.Item>

              <Descriptions.Item label="Enabled">
                <ProField text={enabled ? 'Yes' : 'No'} />
              </Descriptions.Item>
            </Descriptions>
          </ProForm>
        </Skeleton>
      </div>
    </Modal>
  )
}

export default GetInferenceJobModal;