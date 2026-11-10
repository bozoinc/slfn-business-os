// src/middleware/audit-logger.ts
import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

interface AuditLogEntry {
  timestamp: string;
  method: string;
  url: string;
  requestData?: any;
  responseData?: any;
  statusCode?: number;
  error?: string;
}

class AuditLogger {
  private static instance: AuditLogger;
  private axiosInstance: AxiosInstance;
  private logQueue: AuditLogEntry[] = [];
  private isEnabled: boolean = true;

  private constructor() {
    // Create axios instance for sending logs to backend
    this.axiosInstance = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8081',
      timeout: 5000,
    });

    // Check if audit logging is enabled via environment
    this.isEnabled = import.meta.env.VITE_AUDIT_LOGGING_ENABLED === 'true';
  }

  public static getInstance(): AuditLogger {
    if (!AuditLogger.instance) {
      AuditLogger.instance = new AuditLogger();
    }
    return AuditLogger.instance;
  }

  private sanitizeData(data: any): any {
    if (!data) return data;
    
    // Create a copy to avoid modifying original
    const sanitized = JSON.parse(JSON.stringify(data));
    
    // Redact sensitive fields
    const sensitiveFields = ['password', 'token', 'secret', 'key', 'authorization', 'ssn', 'creditcard'];
    
    const redact = (obj: any, path: string = ''): void => {
      if (obj && typeof obj === 'object') {
        Object.keys(obj).forEach(key => {
          const fullPath = `${path}.${key}`.replace(/^\./, '');
          const lowerKey = key.toLowerCase();
          
          if (sensitiveFields.some(field => lowerKey.includes(field))) {
            obj[key] = '[REDACTED]';
          } else if (typeof obj[key] === 'object' && obj[key] !== null) {
            redact(obj[key], fullPath);
          }
        });
      }
    };
    
    redact(sanitized);
    return sanitized;
  }

  public async logRequest(config: InternalAxiosRequestConfig): Promise<InternalAxiosRequestConfig> {
    if (!this.isEnabled) return config;
    
    const logEntry: AuditLogEntry = {
      timestamp: new Date().toISOString(),
      method: config.method?.toUpperCase() || 'UNKNOWN',
      url: config.url || '',
      requestData: this.sanitizeData(config.data),
    };
    
    // Store for pairing with response
    config.metadata = { auditLogEntry: logEntry };
    return config;
  }

  public async logResponse(response: AxiosResponse): Promise<AxiosResponse> {
    if (!this.isEnabled) return response;
    
    const config = response.config;
    if (config?.metadata?.auditLogEntry) {
      const logEntry = config.metadata.auditLogEntry as AuditLogEntry;
      logEntry.statusCode = response.status;
      logEntry.responseData = this.sanitizeData(response.data);
      
      // Add to queue for batch sending
      this.logQueue.push(logEntry);
      
      // Send in batches (every 10 entries or every 5 seconds)
      if (this.logQueue.length >= 10) {
        await this.flushLogs();
      }
    }
    
    return response;
  }

  public async logError(error: AxiosError): Promise<AxiosError> {
    if (!this.isEnabled) return Promise.reject(error);
    
    const config = error.config;
    if (config?.metadata?.auditLogEntry) {
      const logEntry = config.metadata.auditLogEntry as AuditLogEntry;
      logEntry.statusCode = error.response?.status;
      logEntry.responseData = this.sanitizeData(error.response?.data);
      logEntry.error = error.message;
      
      this.logQueue.push(logEntry);
      
      if (this.logQueue.length >= 10) {
        await this.flushLogs();
      }
    }
    
    return Promise.reject(error);
  }

  private async flushLogs(): Promise<void> {
    if (this.logQueue.length === 0 || !this.isEnabled) return;
    
    const logsToSend = [...this.logQueue];
    this.logQueue = [];
    
    try {
      await this.axiosInstance.post('/api/v1/audit-log/batch', {
        logs: logsToSend,
        timestamp: new Date().toISOString()
      });
    } catch (err) {
      // If sending fails, re-queue logs (simple retry mechanism)
      console.warn('Failed to send audit logs, re-queuing:', err);
      this.logQueue = [...logsToSend, ...this.logQueue];
    }
  }

  public async forceFlush(): Promise<void> {
    await this.flushLogs();
  }

  public setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }
}

// Create axios interceptor
export const setupAuditLogging = (axiosInstance: AxiosInstance): void => {
  const logger = AuditLogger.getInstance();
  
  // Request interceptor
  axiosInstance.interceptors.request.use(
    (config) => logger.logRequest(config as InternalAxiosRequestConfig),
    (error) => Promise.reject(error)
  );
  
  // Response interceptor
  axiosInstance.interceptors.response.use(
    (response) => logger.logResponse(response),
    (error) => logger.logError(error as AxiosError)
  );
};

// Export helper functions
export const auditLogger = AuditLogger.getInstance();