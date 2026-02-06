'use client'

import type { FC } from 'react'
import { useTranslation } from 'react-i18next'
import SearchInput from '@/app/components/base/search-input'
import { PortalSelect } from '@/app/components/base/select'

export type UserFiltersProps = {
  search: string
  onSearchChange: (value: string) => void
  roleFilter: string
  onRoleFilterChange: (value: string) => void
  statusFilter: string
  onStatusFilterChange: (value: string) => void
  roleFilterOptions: Array<{ value: string, name: string }>
  statusFilterOptions: Array<{ value: string, name: string }>
}

const UserFilters: FC<UserFiltersProps> = ({
  search,
  onSearchChange,
  roleFilter,
  onRoleFilterChange,
  statusFilter,
  onStatusFilterChange,
  roleFilterOptions,
  statusFilterOptions,
}) => {
  const { t } = useTranslation()

  return (
    <div className="mb-4 flex items-center gap-3">
      <SearchInput
        className="max-w-[400px] flex-1"
        placeholder=""
        value={search}
        onChange={onSearchChange}
      />
      <div className="w-[160px] shrink-0">
        <PortalSelect
          value={roleFilter}
          items={roleFilterOptions}
          onSelect={item => onRoleFilterChange(item.value as string)}
          placeholder={t('admin.filterByRole', { ns: 'custom' })}
        />
      </div>
      <div className="w-[140px] shrink-0">
        <PortalSelect
          value={statusFilter}
          items={statusFilterOptions}
          onSelect={item => onStatusFilterChange(item.value as string)}
          placeholder={t('admin.filterByStatus', { ns: 'custom' })}
        />
      </div>
    </div>
  )
}

export default UserFilters
