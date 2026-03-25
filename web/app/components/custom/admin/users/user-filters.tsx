'use client'

import type { FC } from 'react'
import { useTranslation } from 'react-i18next'
import SearchInput from '@/app/components/base/search-input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/app/components/base/ui/select'

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
        <Select
          value={roleFilter || undefined}
          onValueChange={v => onRoleFilterChange(v ?? '')}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder={t('admin.filterByRole', { ns: 'custom' })} />
          </SelectTrigger>
          <SelectContent>
            {roleFilterOptions.map(opt => (
              <SelectItem key={opt.value} value={opt.value}>{opt.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="w-[140px] shrink-0">
        <Select
          value={statusFilter || undefined}
          onValueChange={v => onStatusFilterChange(v ?? '')}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder={t('admin.filterByStatus', { ns: 'custom' })} />
          </SelectTrigger>
          <SelectContent>
            {statusFilterOptions.map(opt => (
              <SelectItem key={opt.value} value={opt.value}>{opt.name}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}

export default UserFilters
