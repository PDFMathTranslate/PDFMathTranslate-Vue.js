import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
    uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        return apiClient.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    translate(params) {
        const formData = new FormData();
        for (const key in params) {
            if (params[key] !== null && params[key] !== undefined) {
                formData.append(key, params[key]);
            }
        }
        return apiClient.post('/translate', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            }
        });
    },
    getStatus(taskId) {
        return apiClient.get(`/status/${taskId}`);
    },
    getConfig() {
        return apiClient.get('/config');
    },
    downloadTaskResult(taskId) {
        return apiClient.get(`/download_task/${taskId}`, { responseType: 'blob' });
    },
    downloadTaskMono(taskId) {
        return apiClient.get(`/download_task/${taskId}/mono`, { responseType: 'blob' });
    },
    downloadTaskDual(taskId) {
        return apiClient.get(`/download_task/${taskId}/dual`, { responseType: 'blob' });
    }
};
