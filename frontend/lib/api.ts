const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  params?: Record<string, string>
): Promise<T> {
  const url = new URL(`${API_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
  }

  const res = await fetch(url.toString(), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error ${res.status}`);
  }

  return res.json();
}

// ── Dashboard ──────────────────────────────────
export const api = {
  dashboard: {
    get: (userId: string) => apiFetch<any>("/dashboard", {}, { user_id: userId }),
  },

  courses: {
    list: () => apiFetch<any[]>("/courses"),
    get: (id: string) => apiFetch<any>(`/courses/${id}`),
  },

  topics: {
    forCourse: (courseId: string, userId?: string) =>
      apiFetch<any[]>(`/topics/course/${courseId}`, {}, userId ? { user_id: userId } : {}),
    detail: (topicId: string, userId?: string) =>
      apiFetch<any>(`/topics/${topicId}/detail`, {}, userId ? { user_id: userId } : {}),
    updateProgress: (topicId: string, state: string, userId: string) =>
      apiFetch<any>(`/topics/${topicId}/progress?user_id=${userId}`, {
        method: "PUT",
        body: JSON.stringify({ state }),
      }),
    allStates: () => apiFetch<any[]>("/topics/states/all"),
  },

  quizzes: {
    generate: (data: { topic_id: string; topic_title: string; difficulty: string }, userId: string) =>
      apiFetch<any>(`/quizzes/generate?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    forTopic: (topicId: string) => apiFetch<any[]>(`/quizzes/topic/${topicId}`),
    get: (id: string) => apiFetch<any>(`/quizzes/${id}`),
    submitAttempt: (data: { quiz_id: string; answers: Record<string, string> }, userId: string) =>
      apiFetch<any>(`/quizzes/attempt?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    userAttempts: (userId: string) => apiFetch<any[]>(`/quizzes/user/${userId}/attempts`),
  },

  studyPlans: {
    list: (userId: string) => apiFetch<any[]>("/study-plans", {}, { user_id: userId }),
    create: (data: any, userId: string) =>
      apiFetch<any>(`/study-plans?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    get: (id: string, userId: string) => apiFetch<any>(`/study-plans/${id}`, {}, { user_id: userId }),
    updateItem: (itemId: string, completed: boolean) =>
      apiFetch<any>(`/study-plans/items/${itemId}`, {
        method: "PATCH",
        body: JSON.stringify({ completed }),
      }),
    delete: (id: string, userId: string) =>
      apiFetch<any>(`/study-plans/${id}?user_id=${userId}`, { method: "DELETE" }),
  },

  recommendations: {
    get: (userId: string) => apiFetch<any[]>("/recommendations", {}, { user_id: userId }),
  },

  chat: {
    history: (userId: string) => apiFetch<any[]>("/chat/history", {}, { user_id: userId }),
    send: (content: string, userId: string) =>
      apiFetch<any>(`/chat/send?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify({ content }),
      }),
    clear: (userId: string) =>
      apiFetch<any>(`/chat/history?user_id=${userId}`, { method: "DELETE" }),
  },

  notifications: {
    list: (userId: string, unreadOnly = false) =>
      apiFetch<any[]>("/notifications", {}, { user_id: userId, ...(unreadOnly ? { unread_only: "true" } : {}) }),
    unreadCount: (userId: string) => apiFetch<{ unread_count: number }>("/notifications/unread-count", {}, { user_id: userId }),
    markRead: (id: string) => apiFetch<any>(`/notifications/${id}/read`, { method: "PATCH" }),
    markAllRead: (userId: string) =>
      apiFetch<any>(`/notifications/mark-all-read?user_id=${userId}`, { method: "PATCH" }),
  },

  groups: {
    list: (userId?: string) => apiFetch<any[]>("/groups", {}, userId ? { user_id: userId } : {}),
    create: (data: { name: string; description?: string }, userId: string) =>
      apiFetch<any>(`/groups?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
    join: (groupId: string, userId: string) =>
      apiFetch<any>(`/groups/${groupId}/join?user_id=${userId}`, { method: "POST" }),
    leave: (groupId: string, userId: string) =>
      apiFetch<any>(`/groups/${groupId}/leave?user_id=${userId}`, { method: "DELETE" }),
    members: (groupId: string) => apiFetch<any[]>(`/groups/${groupId}/members`),
    leaderboard: (groupId: string) => apiFetch<any[]>(`/groups/${groupId}/leaderboard`),
  },

  predictions: {
    list: (userId: string) => apiFetch<any[]>("/predictions", {}, { user_id: userId }),
    generate: (topicId: string, userId: string) =>
      apiFetch<any>(`/predictions/generate/${topicId}?user_id=${userId}`, { method: "POST" }),
  },

  profiles: {
    get: (userId: string) => apiFetch<any>(`/profiles/${userId}`),
    update: (userId: string, data: any) =>
      apiFetch<any>(`/profiles/${userId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      }),
    achievements: (userId: string) => apiFetch<any[]>(`/profiles/${userId}/achievements`),
  },

  auth: {
    signup: (data: { email: string; password: string; name: string }) =>
      apiFetch<any>("/auth/signup", { method: "POST", body: JSON.stringify(data) }),
    login: (data: { email: string; password: string }) =>
      apiFetch<any>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
    onboarding: (data: any, userId: string) =>
      apiFetch<any>(`/auth/onboarding?user_id=${userId}`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },
};
