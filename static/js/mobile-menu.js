/**
 * 移动端菜单交互逻辑
 * 处理移动端导航菜单的显示/隐藏和交互
 */

(function() {
    'use strict';
    
    // 等待DOM加载完成
    document.addEventListener('DOMContentLoaded', function() {
        const mobileMenu = document.getElementById('mobileMenu');
        const toggleButton = document.querySelector('.mobile-menu-toggle');
        
        if (!mobileMenu || !toggleButton) {
            return;
        }
        
        /**
         * 切换移动端菜单显示状态
         */
        function toggleMobileMenu() {
            if (mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            } else {
                openMobileMenu();
            }
        }
        
        /**
         * 打开移动端菜单
         */
        function openMobileMenu() {
            mobileMenu.classList.add('active');
            toggleButton.innerHTML = '✕';
            // 防止背景滚动
            document.body.style.overflow = 'hidden';
        }
        
        /**
         * 关闭移动端菜单
         */
        function closeMobileMenu() {
            mobileMenu.classList.remove('active');
            toggleButton.innerHTML = '☰';
            // 恢复背景滚动
            document.body.style.overflow = '';
        }
        
        /**
         * 处理菜单按钮点击事件
         */
        function handleToggleClick(e) {
            e.preventDefault();
            e.stopPropagation();
            toggleMobileMenu();
        }
        
        /**
         * 处理点击菜单外部关闭菜单
         */
        function handleDocumentClick(event) {
            if (!mobileMenu.contains(event.target) && 
                !toggleButton.contains(event.target)) {
                closeMobileMenu();
            }
        }
        
        /**
         * 处理菜单项点击后关闭菜单
         */
        function handleMenuLinkClick() {
            closeMobileMenu();
        }
        
        /**
         * 处理键盘事件（ESC键关闭菜单）
         */
        function handleKeyDown(event) {
            if (event.key === 'Escape' && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        }
        
        // 绑定事件监听器
        toggleButton.addEventListener('click', handleToggleClick);
        document.addEventListener('click', handleDocumentClick);
        document.addEventListener('keydown', handleKeyDown);
        
        // 为所有移动端菜单链接绑定点击事件
        const mobileMenuLinks = document.querySelectorAll('.mobile-menu a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', handleMenuLinkClick);
        });
        
        // 处理窗口大小变化
        window.addEventListener('resize', function() {
            // 如果窗口变大，自动关闭移动端菜单
            if (window.innerWidth > 768 && mobileMenu.classList.contains('active')) {
                closeMobileMenu();
            }
        });
    });
})();
