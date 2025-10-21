<?php
/**
 * CyborX Redeem Tool - PHP Version
 * Main Configuration File
 */

// Start session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Environment configuration
define('APP_NAME', 'CyborX Redeem Tool');
define('APP_VERSION', '1.0.0');
define('APP_ENV', $_ENV['APP_ENV'] ?? 'development');
define('APP_DEBUG', APP_ENV === 'development');

// Paths
define('BASE_PATH', dirname(__DIR__));
define('PUBLIC_PATH', BASE_PATH . '/public');
define('SRC_PATH', BASE_PATH . '/src');
define('TEMPLATES_PATH', BASE_PATH . '/templates');
define('ASSETS_PATH', BASE_PATH . '/assets');

// URLs
define('BASE_URL', $_ENV['BASE_URL'] ?? 'http://localhost:8000');
define('ASSETS_URL', BASE_URL . '/assets');

// CyborX API Configuration
define('CYBORX_BASE_URL', 'https://cyborx.net');
define('CYBORX_REDEEM_URL', CYBORX_BASE_URL . '/api/redeem_submit.php');
define('CYBORX_DASHBOARD_URL', CYBORX_BASE_URL . '/app/dashboard');

// Session Configuration
define('SESSION_LIFETIME', 3600); // 1 hour
define('SESSION_NAME', 'CYBORX_REDEEM_SESSION');

// Request Configuration
define('REQUEST_TIMEOUT', 30);
define('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36');

// Security
define('CSRF_TOKEN_NAME', '_csrf_token');
define('MAX_CODES_PER_REQUEST', 1000);
define('MAX_FILE_SIZE', 1024 * 1024); // 1MB

// Development helpers
if (APP_DEBUG) {
    error_reporting(E_ALL);
    ini_set('display_errors', 1);
    ini_set('log_errors', 1);
}

// Autoloader
require_once BASE_PATH . '/vendor/autoload.php';

// Helper functions
require_once BASE_PATH . '/src/helpers.php';