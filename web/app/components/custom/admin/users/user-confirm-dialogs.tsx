'use client'

import type { FC } from 'react'
import type { UserStatus } from '@/models/custom/admin'
import { useTranslation } from 'react-i18next'
import {
  AlertDialog,
  AlertDialogActions,
  AlertDialogCancelButton,
  AlertDialogConfirmButton,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogTitle,
} from '@/app/components/base/ui/alert-dialog'

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
      <AlertDialog open={showStatusConfirm} onOpenChange={open => !open && onCancelStatusToggle()}>
        <AlertDialogContent>
          <div className="flex flex-col items-start gap-2 self-stretch pb-4 pl-6 pr-6 pt-6">
            <AlertDialogTitle className="w-full text-text-primary title-2xl-semi-bold">
              {t('admin.confirmDisableUserTitle', { ns: 'custom' })}
            </AlertDialogTitle>
            <AlertDialogDescription className="w-full whitespace-pre-wrap break-words text-text-tertiary system-md-regular">
              {t('admin.confirmDisableUser', { ns: 'custom', name: userToToggle?.name || '' })}
            </AlertDialogDescription>
          </div>
          <AlertDialogActions>
            <AlertDialogCancelButton disabled={isUpdatingStatus}>
              {t('operation.cancel', { ns: 'common' })}
            </AlertDialogCancelButton>
            <AlertDialogConfirmButton loading={isUpdatingStatus} disabled={isUpdatingStatus} onClick={onConfirmStatusToggle}>
              {t('operation.confirm', { ns: 'common' })}
            </AlertDialogConfirmButton>
          </AlertDialogActions>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showDeleteConfirm} onOpenChange={open => !open && onCancelDelete()}>
        <AlertDialogContent>
          <div className="flex flex-col items-start gap-2 self-stretch pb-4 pl-6 pr-6 pt-6">
            <AlertDialogTitle className="w-full text-text-primary title-2xl-semi-bold">
              {t('admin.confirmDeleteUserTitle', { ns: 'custom' })}
            </AlertDialogTitle>
            <AlertDialogDescription className="w-full whitespace-pre-wrap break-words text-text-tertiary system-md-regular">
              {t('admin.confirmDeleteUser', { ns: 'custom', name: userToDelete?.name || '' })}
            </AlertDialogDescription>
          </div>
          <AlertDialogActions>
            <AlertDialogCancelButton disabled={isDeleting}>
              {t('operation.cancel', { ns: 'common' })}
            </AlertDialogCancelButton>
            <AlertDialogConfirmButton loading={isDeleting} disabled={isDeleting} onClick={onConfirmDelete}>
              {t('operation.confirm', { ns: 'common' })}
            </AlertDialogConfirmButton>
          </AlertDialogActions>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showBatchConfirm} onOpenChange={open => !open && onCancelBatchAction()}>
        <AlertDialogContent>
          <div className="flex flex-col items-start gap-2 self-stretch pb-4 pl-6 pr-6 pt-6">
            <AlertDialogTitle className="w-full text-text-primary title-2xl-semi-bold">
              {batchAction === 'enable'
                ? t('admin.confirmBatchEnableTitle', { ns: 'custom' })
                : batchAction === 'disable'
                  ? t('admin.confirmBatchDisableTitle', { ns: 'custom' })
                  : t('admin.confirmBatchDeleteTitle', { ns: 'custom' })}
            </AlertDialogTitle>
            <AlertDialogDescription className="w-full whitespace-pre-wrap break-words text-text-tertiary system-md-regular">
              {batchAction === 'enable'
                ? t('admin.confirmBatchEnable', { ns: 'custom', count: selectedCount })
                : batchAction === 'disable'
                  ? t('admin.confirmBatchDisable', { ns: 'custom', count: selectedCount })
                  : t('admin.confirmBatchDelete', { ns: 'custom', count: selectedCount })}
            </AlertDialogDescription>
          </div>
          <AlertDialogActions>
            <AlertDialogCancelButton disabled={isBatchProcessing}>
              {t('operation.cancel', { ns: 'common' })}
            </AlertDialogCancelButton>
            <AlertDialogConfirmButton
              loading={isBatchProcessing}
              disabled={isBatchProcessing}
              destructive={batchAction === 'delete'}
              onClick={onConfirmBatchAction}
            >
              {t('operation.confirm', { ns: 'common' })}
            </AlertDialogConfirmButton>
          </AlertDialogActions>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

export default UserConfirmDialogs
