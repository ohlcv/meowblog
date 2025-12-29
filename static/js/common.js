/**
 * 通用JavaScript功能
 * 包含项目中常用的JavaScript工具函数和交互逻辑
 */

(function() {
    'use strict';
    
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        
        /**
         * 初始化所有通用功能
         */
        function init() {
            initSmoothScroll();
            initTooltips();
            initFormValidation();
            initLoadingStates();
            initCopyToClipboard();
            initGlobalMessages();
            initCopyMarkdown();
        }
        
        /**
         * 平滑滚动功能
         */
        function initSmoothScroll() {
            const links = document.querySelectorAll('a[href^="#"]');
            
            links.forEach(link => {
                link.addEventListener('click', function(e) {
                    const targetId = this.getAttribute('href');
                    const targetElement = document.querySelector(targetId);
                    
                    if (targetElement) {
                        e.preventDefault();
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        }
        
        /**
         * 工具提示功能
         */
        function initTooltips() {
            const tooltipElements = document.querySelectorAll('[data-tooltip]');
            
            tooltipElements.forEach(element => {
                element.addEventListener('mouseenter', showTooltip);
                element.addEventListener('mouseleave', hideTooltip);
            });
        }
        
        function showTooltip(e) {
            const text = e.target.getAttribute('data-tooltip');
            if (!text) return;
            
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = text;
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.875rem;
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s ease;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = e.target.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            // 显示工具提示
            setTimeout(() => {
                tooltip.style.opacity = '1';
            }, 10);
            
            e.target._tooltip = tooltip;
        }
        
        function hideTooltip(e) {
            if (e.target._tooltip) {
                e.target._tooltip.remove();
                delete e.target._tooltip;
            }
        }
        
        /**
         * 表单验证功能
         */
        function initFormValidation() {
            const forms = document.querySelectorAll('form[data-validate]');
            
            forms.forEach(form => {
                form.addEventListener('submit', function(e) {
                    if (!validateForm(this)) {
                        e.preventDefault();
                    }
                });
            });
        }
        
        function validateForm(form) {
            let isValid = true;
            const requiredFields = form.querySelectorAll('[required]');
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    showFieldError(field, '此字段为必填项');
                    isValid = false;
                } else {
                    clearFieldError(field);
                }
            });
            
            return isValid;
        }
        
        function showFieldError(field, message) {
            clearFieldError(field);
            
            const errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            errorElement.textContent = message;
            
            field.parentNode.appendChild(errorElement);
            field.classList.add('form-control-error');
        }
        
        function clearFieldError(field) {
            const existingError = field.parentNode.querySelector('.form-error');
            if (existingError) {
                existingError.remove();
            }
            field.classList.remove('form-control-error');
        }
        
        /**
         * 加载状态功能
         */
        function initLoadingStates() {
            const loadingButtons = document.querySelectorAll('[data-loading]');
            
            loadingButtons.forEach(button => {
                button.addEventListener('click', function() {
                    setButtonLoading(this, true);
                    
                    // 模拟异步操作完成后恢复按钮状态
                    setTimeout(() => {
                        setButtonLoading(this, false);
                    }, 2000);
                });
            });
        }
        
        function setButtonLoading(button, isLoading) {
            if (isLoading) {
                button.classList.add('btn-loading');
                button.disabled = true;
                button.setAttribute('data-original-text', button.textContent);
                button.textContent = '加载中...';
            } else {
                button.classList.remove('btn-loading');
                button.disabled = false;
                button.textContent = button.getAttribute('data-original-text') || button.textContent;
            }
        }
        
        /**
         * 复制到剪贴板功能
         */
        function initCopyToClipboard() {
            const copyButtons = document.querySelectorAll('[data-copy]');
            
            copyButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const textToCopy = this.getAttribute('data-copy');
                    copyToClipboard(textToCopy, this);
                });
            });
        }
        
        function copyToClipboard(text, button) {
            if (navigator.clipboard && window.isSecureContext) {
                // 使用现代 Clipboard API
                navigator.clipboard.writeText(text).then(() => {
                    showCopySuccess(button);
                }).catch(() => {
                    fallbackCopyToClipboard(text, button);
                });
            } else {
                // 降级方案
                fallbackCopyToClipboard(text, button);
            }
        }
        
        function fallbackCopyToClipboard(text, button) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                document.execCommand('copy');
                showCopySuccess(button);
            } catch (err) {
                showCopyError(button);
            }
            
            document.body.removeChild(textArea);
        }
        
        function showCopySuccess(button) {
            const originalText = button.textContent;
            button.textContent = '已复制!';
            button.style.background = 'var(--success-color)';
            
            // 显示toast消息
            showToastMessage('文章已复制为Markdown格式！', 'success');
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
            }, 2000);
        }
        
        function showCopyError(button) {
            const originalText = button.textContent;
            button.textContent = '复制失败';
            button.style.background = 'var(--danger-color)';
            
            setTimeout(() => {
                button.textContent = originalText;
                button.style.background = '';
            }, 2000);
        }
        
        /**
         * 防抖函数
         */
        function debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
        
        /**
         * 节流函数
         */
        function throttle(func, limit) {
            let inThrottle;
            return function() {
                const args = arguments;
                const context = this;
                if (!inThrottle) {
                    func.apply(context, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        }
        
        /**
         * 全局消息提示系统
         */
        function initGlobalMessages() {
            // 将Django消息转换为右上角toast提示
            const djangoMessages = document.querySelectorAll('.alert, .message-container .alert');
            
            djangoMessages.forEach(messageElement => {
                const messageText = messageElement.textContent.trim();
                const messageType = getMessageType(messageElement);
                
                // 显示toast消息
                showToastMessage(messageText, messageType);
                
                // 隐藏原始消息
                messageElement.style.display = 'none';
            });
        }
        
        function getMessageType(element) {
            if (element.classList.contains('alert-success') || element.classList.contains('message-success')) {
                return 'success';
            } else if (element.classList.contains('alert-error') || element.classList.contains('message-error')) {
                return 'error';
            } else if (element.classList.contains('alert-warning') || element.classList.contains('message-warning')) {
                return 'warning';
            } else if (element.classList.contains('alert-info') || element.classList.contains('message-info')) {
                return 'info';
            }
            return 'info';
        }
        
        function showToastMessage(message, type = 'info') {
            // 创建消息容器（如果不存在）
            let messageContainer = document.getElementById('toast-message-container');
            if (!messageContainer) {
                messageContainer = document.createElement('div');
                messageContainer.id = 'toast-message-container';
                messageContainer.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 10000;
                    pointer-events: none;
                `;
                document.body.appendChild(messageContainer);
            }
            
            // 创建消息元素
            const messageDiv = document.createElement('div');
            messageDiv.className = `toast-message toast-${type}`;
            messageDiv.textContent = message;
            messageDiv.style.cssText = `
                padding: 12px 20px;
                margin-bottom: 10px;
                border-radius: 8px;
                color: white;
                font-weight: 500;
                font-size: 14px;
                max-width: 350px;
                word-wrap: break-word;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s ease;
                pointer-events: auto;
                cursor: pointer;
            `;
            
            // 根据类型设置样式
            const typeStyles = {
                success: 'background: linear-gradient(135deg, #28a745 0%, #20c997 100%);',
                error: 'background: linear-gradient(135deg, #dc3545 0%, #e74c3c 100%);',
                warning: 'background: linear-gradient(135deg, #ffc107 0%, #fd7e14 100%);',
                info: 'background: linear-gradient(135deg, #17a2b8 0%, #6f42c1 100%);'
            };
            
            messageDiv.style.cssText += typeStyles[type] || typeStyles.info;
            
            // 添加到容器
            messageContainer.appendChild(messageDiv);
            
            // 显示动画
            setTimeout(() => {
                messageDiv.style.transform = 'translateX(0)';
                messageDiv.style.opacity = '1';
            }, 10);
            
            // 点击关闭
            messageDiv.addEventListener('click', () => {
                hideToastMessage(messageDiv);
            });
            
            // 自动隐藏
            setTimeout(() => {
                hideToastMessage(messageDiv);
            }, 4000);
        }
        
        function hideToastMessage(messageDiv) {
            messageDiv.style.transform = 'translateX(100%)';
            messageDiv.style.opacity = '0';
            
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.parentNode.removeChild(messageDiv);
                }
            }, 300);
        }
        
        /**
         * HTML到Markdown转换器
         */
        function htmlToMarkdown(html) {
            // 创建一个临时的div元素来解析HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // 递归转换函数
            function convertNode(node) {
                if (node.nodeType === Node.TEXT_NODE) {
                    return node.textContent;
                }
                
                if (node.nodeType !== Node.ELEMENT_NODE) {
                    return '';
                }
                
                const tagName = node.tagName.toLowerCase();
                const children = Array.from(node.childNodes).map(convertNode).join('');
                
                switch (tagName) {
                    case 'h1':
                        return `# ${children}\n\n`;
                    case 'h2':
                        return `## ${children}\n\n`;
                    case 'h3':
                        return `### ${children}\n\n`;
                    case 'h4':
                        return `#### ${children}\n\n`;
                    case 'h5':
                        return `##### ${children}\n\n`;
                    case 'h6':
                        return `###### ${children}\n\n`;
                    case 'p':
                        return `${children}\n\n`;
                    case 'br':
                        return '\n';
                    case 'strong':
                    case 'b':
                        return `**${children}**`;
                    case 'em':
                    case 'i':
                        return `*${children}*`;
                    case 'code':
                        return `\`${children}\``;
                    case 'pre':
                        return `\`\`\`\n${children}\n\`\`\`\n\n`;
                    case 'blockquote':
                        return `> ${children.replace(/\n/g, '\n> ')}\n\n`;
                    case 'ul':
                        return `${children}\n`;
                    case 'ol':
                        return `${children}\n`;
                    case 'li':
                        const parent = node.parentElement;
                        if (parent && parent.tagName.toLowerCase() === 'ol') {
                            const index = Array.from(parent.children).indexOf(node) + 1;
                            return `${index}. ${children}\n`;
                        } else {
                            return `- ${children}\n`;
                        }
                    case 'a':
                        const href = node.getAttribute('href') || '';
                        return `[${children}](${href})`;
                    case 'img':
                        const src = node.getAttribute('src') || '';
                        const alt = node.getAttribute('alt') || '';
                        return `![${alt}](${src})`;
                    case 'hr':
                        return '---\n\n';
                    case 'table':
                        return convertTable(node);
                    case 'tr':
                        return convertTableRow(node);
                    case 'th':
                    case 'td':
                        return `| ${children} `;
                    default:
                        return children;
                }
            }
            
            // 转换表格
            function convertTable(table) {
                const rows = Array.from(table.querySelectorAll('tr'));
                if (rows.length === 0) return '';
                
                let result = '';
                
                // 表头
                const headerRow = rows[0];
                const headerCells = Array.from(headerRow.querySelectorAll('th, td'));
                result += '| ' + headerCells.map(cell => convertNode(cell).trim()).join(' | ') + ' |\n';
                result += '| ' + headerCells.map(() => '---').join(' | ') + ' |\n';
                
                // 数据行
                for (let i = 1; i < rows.length; i++) {
                    const cells = Array.from(rows[i].querySelectorAll('td, th'));
                    result += '| ' + cells.map(cell => convertNode(cell).trim()).join(' | ') + ' |\n';
                }
                
                return result + '\n';
            }
            
            // 转换表格行
            function convertTableRow(row) {
                const cells = Array.from(row.querySelectorAll('th, td'));
                return '| ' + cells.map(cell => convertNode(cell).trim()).join(' | ') + ' |\n';
            }
            
            return convertNode(tempDiv).trim();
        }
        
        /**
         * 复制文章为Markdown格式
         */
        function copyPostAsMarkdown(title, content, author, created) {
            // 清理HTML内容，移除转义字符
            const cleanContent = content
                .replace(/\\u000D\\u000A/g, '\n')  // 替换换行符
                .replace(/\\u002D/g, '-')          // 替换连字符
                .replace(/\\u0027/g, "'")          // 替换单引号
                .replace(/\\u0022/g, '"')          // 替换双引号
                .replace(/\\u003C/g, '<')          // 替换小于号
                .replace(/\\u003E/g, '>')          // 替换大于号
                .replace(/\\u0026/g, '&')          // 替换&符号
                .replace(/\\u0060/g, '`')          // 替换反引号
                .replace(/\\u005C/g, '\\');        // 替换反斜杠
            
            const markdownContent = htmlToMarkdown(cleanContent);
            
            const fullMarkdown = `# ${title}

**作者**: ${author}  
**发布时间**: ${created}

---

${markdownContent}

---

*本文来自 [Meow Blog](https://meowsite.cn) - 一个专注于知识分享的博客平台*`;
            
            copyToClipboard(fullMarkdown, document.getElementById('copy-md-btn'));
        }
        
        /**
         * 初始化复制Markdown功能
         */
        function initCopyMarkdown() {
            // 延迟执行，确保DOM完全加载
            setTimeout(function() {
                const copyBtn = document.getElementById('copy-md-btn');
                
                if (copyBtn) {
                    copyBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        
                        const title = this.getAttribute('data-post-title');
                        const content = this.getAttribute('data-post-content');
                        const author = this.getAttribute('data-post-author');
                        const created = this.getAttribute('data-post-created');
                        
                        copyPostAsMarkdown(title, content, author, created);
                    });
                }
            }, 1000);
        }
        
        // 初始化所有功能
        init();
        
        // 将工具函数暴露到全局作用域
        window.MeowSite = {
            debounce: debounce,
            throttle: throttle,
            setButtonLoading: setButtonLoading,
            copyToClipboard: copyToClipboard,
            showToastMessage: showToastMessage,
            htmlToMarkdown: htmlToMarkdown,
            copyPostAsMarkdown: copyPostAsMarkdown
        };
    });
})();
