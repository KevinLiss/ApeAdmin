/**
 * AI 会议助手插件 - 前端 API 封装
 * 全部接口走 /api/v1/aimeeting/*
 */
import request from './request'

// ---------- 会议管理 ----------
export const getMeetings = (params: any) =>
  request.get('/aimeeting/meetings', { params })
export const getMeetingDetail = (id: number) =>
  request.get(`/aimeeting/meetings/${id}`)
export const createMeeting = (data: any) =>
  request.post('/aimeeting/meetings', data)
export const updateMeeting = (id: number, data: any) =>
  request.put(`/aimeeting/meetings/${id}`, data)
export const updateMeetingStatus = (id: number, status: string) =>
  request.put(`/aimeeting/meetings/${id}/status`, { status })
export const deleteMeeting = (id: number) =>
  request.delete(`/aimeeting/meetings/${id}`)
export const batchDeleteMeetings = (ids: number[]) =>
  request.post('/aimeeting/meetings/batch-delete', { ids })

// ---------- 运行环境自检（只读诊断） ----------
export const checkEnv = () =>
  request.get('/aimeeting/env/check')

// ---------- 录音转写记录（管理端查看） ----------
export const getMeetingRecords = (meetingId: number) =>
  request.get(`/aimeeting/meetings/${meetingId}/records`)

// ---------- 会议纪要 / 总结 ----------
export const getMeetingMinutes = (meetingId: number) =>
  request.get(`/aimeeting/meetings/${meetingId}/minutes`)
export const generateMeetingMinutes = (meetingId: number) =>
  request.post(`/aimeeting/meetings/${meetingId}/minutes/generate`)
// ---------- 数据面板 ----------
export const getDashboardStats = () =>
  request.get('/aimeeting/dashboard/stats')
