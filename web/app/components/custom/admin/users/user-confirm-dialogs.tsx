'use client'

import type { FC } from 'react'
import type { UserStatus } from '@/models/custom/admin'
import { useTranslation } from 'react-i18next'
import Confirm from '@/app/components/base/confirm'

type UserConfirmDialogsProps = {
  showStatusConfirm: boolean
  userToToggle: { id: string, name: string, status: UserStatus } | null
  onConfirmStatusToggle: () => void
  onCancelStatusToggle: () => void
  isUpdatingStatus: boolean

  showDeleteConfirm: boolean
  userToDelete: { id: string, name: string } | null
  onConfirmDelete: () => void
  onCancelDelete: () => void
  isDeleting: boolean

  showBatchConfirm: boolean
  batchAction: 'enable' | 'disable' | 'delete' | null
  selectedCount: number
  onConfirmBatchAction: () => void
  onCancelBatchAction: () => void
  isBatchProcessing: boolean
}

const UserConfirmDialogs: FC<UserConfirmDialogsProps> = ({
  showStatusConfirm,
  userToToggle,
  onConfirmStatusToggle,
  onCancelStatusToggle,
  isUpdatingStatus,
  showDeleteConfirm,
  userToDelete,
  onConfirmDelete,
  onCancelDelete,
  isDeleting,
  showBatchConfirm,
  batchAction,
  selectedCount,
  onConfirmBatchAction,
  onCancelBatchAction,
  isBatchProcessing,
}) => {
  const { t } = useTranslation()

  return (
    <>
      <Confirm
        isShow={showStatusConfirm}
        type="danger"
        title={t('admin.confirmDisableUserTitle', { ns: 'custom' })}
        content={t('admin.confirmDisableUser', { ns: 'custom', name: userToToggle?.name || '' })}
        onConfirm={onConfirmStatusToggle}
        onCancel={onCancelStatusToggle}
        isLoading={isUpdatingStatus}
      />

      <Confirm
        isShow={showDeleteConfirm}
        type="danger"
        title={t('admin.confirmDeleteUserTitle', { ns: 'custom' })}
        content={t('admin.confirmDeleteUser', { ns: 'custom', name: userToDelete?.name || '' })}
        onConfirm={onConfirmDelete}
        onCancel={onCancelDelete}
        isLoading={isDeleting}
      />

      <Confirm
        isShow={showBatchConfirm}
        type={batchAction === 'delete' ? 'danger' : 'warning'}
        title={
          batchAction === 'enable'
            ? t('admin.confirmBatchEnableTitle', { ns: 'custom' })
            : batchAction === 'disable'
              ? t('admin.confirmBatchDisableTitle', { ns: 'custom' })
              : t('admin.confirmBatchDeleteTitle', { ns: 'custom' })
        }
        content={
          batchAction === 'enable'
            ? t('admin.confirmBatchEnable', { ns: 'custom', count: selectedCount })
            : batchAction === 'disable'
              ? t('admin.confirmBatchDisable', { ns: 'custom', count: selectedCount })
              : t('admin.confirmBatchDelete', { ns: 'custom', count: selectedCount })
        }
        onConfirm={onConfirmBatchAction}
        onCancel={onCancelBatchAction}
        isLoading={isBatchProcessing}
      />
    </>
  )
}

export default UserConfirmDialogs
