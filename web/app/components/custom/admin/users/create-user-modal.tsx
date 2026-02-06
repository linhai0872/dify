'use client'

import type { FC } from 'react'
import type { SystemRole } from '@/models/custom/admin'
import { useCallback, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import Button from '@/app/components/base/button'
import Input from '@/app/components/base/input'
import Modal from '@/app/components/base/modal'
import { PortalSelect } from '@/app/components/base/select'

export type CreateUserModalProps = {
  isShow: boolean
  onClose: () => void
  onSubmit: (data: { name: string, email: string, password: string, systemRole: SystemRole }) => void
  isLoading: boolean
}

const EMAIL_REGEX = /^[^\s@]+@[^\s@][^\s.@]*\.[^\s@]+$/
const MIN_PASSWORD_LENGTH = 8
// Backend requires letters + numbers: ^(?=.*[a-zA-Z])(?=.*\d).{8,}$
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*\d).{8,}$/i

const CreateUserModal: FC<CreateUserModalProps> = ({
  isShow,
  onClose,
  onSubmit,
  isLoading,
}) => {
  const { t } = useTranslation()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<SystemRole>('user')
  const [touched, setTouched] = useState({ name: false, email: false, password: false })

  const errors = useMemo(() => ({
    name: touched.name && !name.trim() ? t('admin.userName', { ns: 'custom' }) : '',
    email: touched.email && !EMAIL_REGEX.test(email) ? t('admin.invalidEmail', { ns: 'custom' }) : '',
    password: touched.password && (password.length < MIN_PASSWORD_LENGTH || !PASSWORD_REGEX.test(password))
      ? t('admin.passwordRequirement', { ns: 'custom' })
      : '',
  }), [name, email, password, touched, t])

  const isValid = useMemo(() => {
    return name.trim().length > 0
      && EMAIL_REGEX.test(email)
      && PASSWORD_REGEX.test(password)
  }, [name, email, password])

  const handleClose = useCallback(() => {
    setName('')
    setEmail('')
    setPassword('')
    setRole('user')
    setTouched({ name: false, email: false, password: false })
    onClose()
  }, [onClose])

  const handleSubmit = useCallback(() => {
    if (!isValid)
      return
    onSubmit({ name: name.trim(), email: email.trim(), password, systemRole: role })
  }, [isValid, name, email, password, role, onSubmit])

  return (
    <Modal
      isShow={isShow}
      onClose={handleClose}
      title={t('admin.createUser', { ns: 'custom' })}
      closable
    >
      <div className="mt-4 space-y-4">
        <div>
          <label className="system-sm-medium mb-2 block text-text-secondary">
            {t('admin.userName', { ns: 'custom' })}
          </label>
          <Input
            value={name}
            onChange={e => setName(e.target.value)}
            onBlur={() => setTouched(prev => ({ ...prev, name: true }))}
            placeholder={t('admin.userNamePlaceholder', { ns: 'custom' })}
          />
          {errors.name && (
            <p className="system-xs-regular mt-1 text-text-destructive">{errors.name}</p>
          )}
        </div>
        <div>
          <label className="system-sm-medium mb-2 block text-text-secondary">
            {t('admin.userEmail', { ns: 'custom' })}
          </label>
          <Input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            onBlur={() => setTouched(prev => ({ ...prev, email: true }))}
            placeholder={t('admin.userEmailPlaceholder', { ns: 'custom' })}
          />
          {errors.email && (
            <p className="system-xs-regular mt-1 text-text-destructive">{errors.email}</p>
          )}
        </div>
        <div>
          <label className="system-sm-medium mb-2 block text-text-secondary">
            {t('admin.userPassword', { ns: 'custom' })}
          </label>
          <Input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onBlur={() => setTouched(prev => ({ ...prev, password: true }))}
            placeholder={t('admin.userPasswordPlaceholder', { ns: 'custom' })}
          />
          <div className="mt-1 flex items-center justify-between">
            {errors.password
              ? <p className="system-xs-regular text-text-destructive">{errors.password}</p>
              : <span />}
            <span className="system-xs-regular text-text-quaternary">
              {password.length}
              /
              {MIN_PASSWORD_LENGTH}
              +
            </span>
          </div>
        </div>
        <div>
          <label className="system-sm-medium mb-2 block text-text-secondary">
            {t('admin.systemRoleLabel', { ns: 'custom' })}
          </label>
          <PortalSelect
            value={role}
            items={[
              { value: 'user', name: t('admin.systemRoleUser', { ns: 'custom' }) },
              { value: 'tenant_manager', name: t('admin.systemRoleTenantManager', { ns: 'custom' }) },
              { value: 'system_admin', name: t('admin.systemRoleSystemAdmin', { ns: 'custom' }) },
            ]}
            onSelect={item => setRole(item.value as SystemRole)}
            popupClassName="w-full !z-[70]"
          />
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={handleClose}>
            {t('admin.cancel', { ns: 'custom' })}
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!isValid || isLoading}
            loading={isLoading}
          >
            {t('admin.createUser', { ns: 'custom' })}
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default CreateUserModal
