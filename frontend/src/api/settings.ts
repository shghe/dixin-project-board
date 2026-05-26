import { get, put } from './request'

export interface PersonnelWages {
  事业人员: number
  企业人员: number
  派遣人员: number
}

export const settingsApi = {
  getWages: () => get<PersonnelWages>('/settings/wages'),
  updateWages: (data: PersonnelWages) => put<{ message: string }>('/settings/wages', data),
}
