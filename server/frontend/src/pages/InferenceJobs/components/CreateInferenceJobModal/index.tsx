import { ProForm, ProFormInstance, ProFormSelect, ProFormText } from '@ant-design/pro-components';
import { useModel, useRequest } from '@umijs/max';
import { Modal } from 'antd';
import * as React from 'react';
import { createInferenceJob } from '../../services';

const createInferenceJobModal = ({
  visible,
  onClose,
}) => {
  const formRef = React.useRef<ProFormInstance>();
  const { getModels } = useModel('global');

  const { run, loading } = useRequest(createInferenceJob, {
    manual: true,
  })

  const handleSubmit = async () => {
    const values = await formRef.current?.validateFields();
    await run(values);
    onClose();
    getModels.run()
  }

  return (
    <Modal
      title="InferenceJob"
      open={visible}
      onCancel={onClose}
      confirmLoading={loading}
      onOk={handleSubmit}
      destroyOnClose
    >
      <ProForm
        formRef={formRef}
        requiredMark={false}
        submitter={{
          render: () => null
        }}
        initialValues={{
          status: 'verified',

        }}
      >
        <ProForm.Group>
          <ProFormText
            width="lg"
            name="name"
            label="Job Name"
            placeholder="Job Name"
            rules={[
              {
                required: true,
                message: 'Missing Job Name'
              }
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="model_id"
            label="Model ID"
            placeholder="Model ID"
            rules={[
              {
                required: true,
                message: 'Missing Model ID'
              }
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormSelect
            width="lg"
            name="status"
            label="Status"
            placeholder="Select"
            rules={[
              {
                required: true,
                message: 'Enter Select'
              }
            ]}
            options={[
              {
                value: 'verified',
                label: 'verified',
              },
              {
                value: 'unverified',
                label: 'unverified',
              },
              {
                value: 'verification_failed',
                label: 'verification_failed',
              },
            ]}
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="description"
            label="Description"
            placeholder="Description"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="min_workers"
            label="Min Workers"
            placeholder="0"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="max_workers"
            label="Max Workers"
            placeholder="0"
          />
        </ProForm.Group>

        <ProForm.Group>
          <ProFormText
            width="lg"
            name="desired_workers"
            label="Desired Workers"
            placeholder="0"
          />
        </ProForm.Group>
        
      </ProForm>
    </Modal>
  );
}
 
export default createInferenceJobModal;