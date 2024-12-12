 
# utils/monitoring.py
import psutil
import time
import logging
import torch
import threading
from typing import Dict, Any
from collections import defaultdict

class SystemMonitor:
    """系統監控管理器"""
    def __init__(self):
        self.metrics = defaultdict(list)
        self.alerts = []
        self.error_log = []
        self.monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(__name__)
        
    def start_monitoring(self):
        """開始系統監控"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.logger.info("System monitoring started")
        
    def stop_monitoring(self):
        """停止系統監控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.logger.info("System monitoring stopped")
        
    def _monitor_loop(self):
        """監控循環"""
        while self.monitoring:
            try:
                self._collect_metrics()
                self._check_thresholds()
                time.sleep(30)  # 每30秒檢查一次
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                
    def _collect_metrics(self):
        """收集系統指標"""
        try:
            # CPU使用率
            self.record_metric('cpu_usage', psutil.cpu_percent())
 
            memory = psutil.virtual_memory()
            self.record_metric('memory_usage', memory.percent)
            
            # 磁碟使用
            disk = psutil.disk_usage('/')
            self.record_metric('disk_usage', disk.percent)
            
            # GPU使用率（如果可用）
            if torch.cuda.is_available():
                try:
                    gpu_info = self.get_gpu_info()
                    self.record_metric('gpu_memory', gpu_info['memory_used'])
                    self.record_metric('gpu_utilization', gpu_info['utilization'])
                except Exception as e:
                    self.logger.error(f"Error collecting GPU metrics: {e}")
        
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")

    def get_gpu_info(self) -> Dict[str, float]:
        """獲取GPU信息"""
        if not torch.cuda.is_available():
            return {'memory_used': 0, 'utilization': 0}
            
        try:
            memory_used = torch.cuda.memory_allocated() / 1024**3  # GB
            memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            utilization = (memory_used / memory_total) * 100
            
            return {
                'memory_used': memory_used,
                'utilization': utilization
            }
        except Exception as e:
            self.logger.error(f"Error getting GPU info: {e}")
            return {'memory_used': 0, 'utilization': 0}

    def record_metric(self, metric_name: str, value: float):
        """記錄系統指標"""
        self.metrics[metric_name].append({
            'timestamp': time.time(),
            'value': value
        })
        
        # 保持最近24小時的數據
        cutoff_time = time.time() - 86400
        self.metrics[metric_name] = [
            m for m in self.metrics[metric_name]
            if m['timestamp'] > cutoff_time
        ]

    def _check_thresholds(self):
        """檢查系統指標閾值"""
        thresholds = {
            'cpu_usage': 90,
            'memory_usage': 90,
            'disk_usage': 90,
            'gpu_memory': 90,
            'gpu_utilization': 95
        }
        
        for metric, limit in thresholds.items():
            if metric in self.metrics and self.metrics[metric]:
                current_value = self.metrics[metric][-1]['value']
                if current_value > limit:
                    self._create_alert(
                        f"{metric} exceeds threshold: {current_value:.1f}%",
                        severity='warning' if current_value < limit + 5 else 'critical'
                    )

    def _create_alert(self, message: str, severity: str = 'warning'):
        """創建系統警告"""
        alert = {
            'timestamp': time.time(),
            'message': message,
            'severity': severity
        }
        self.alerts.append(alert)
        self.logger.warning(f"System alert: {message}")

    def get_system_status(self) -> Dict[str, Any]:
        """獲取系統狀態報告"""
        try:
            status_report = {
                'metrics': {
                    k: [{'time': m['timestamp'], 'value': m['value']} 
                       for m in v[-10:]]  # 最近10個數據點
                    for k, v in self.metrics.items()
                },
                'alerts': self.alerts[-5:],  # 最近5個警告
                'errors': self.error_log[-5:],  # 最近5個錯誤
                'status': self._determine_system_status(),
                'summary': self._generate_summary()
            }
            return status_report
        except Exception as e:
            self.logger.error(f"Error generating status report: {e}")
            return {'status': 'error', 'message': str(e)}

    def _determine_system_status(self) -> str:
        """確定系統狀態"""
        if not self.alerts:
            return 'healthy'
        
        critical_alerts = [a for a in self.alerts[-10:] 
                         if a['severity'] == 'critical']
        if critical_alerts:
            return 'critical'
            
        recent_warnings = [a for a in self.alerts[-10:] 
                         if a['severity'] == 'warning']
        if len(recent_warnings) >= 3:
            return 'warning'
            
        return 'stable'

    def _generate_summary(self) -> Dict[str, Any]:
        """生成系統摘要"""
        try:
            if not self.metrics:
                return {}
                
            summary = {}
            for metric, values in self.metrics.items():
                if values:
                    recent_values = [v['value'] for v in values[-60:]]  # 最近60個數據點
                    summary[metric] = {
                        'current': values[-1]['value'],
                        'average': sum(recent_values) / len(recent_values),
                        'max': max(recent_values),
                        'min': min(recent_values)
                    }
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return {}   